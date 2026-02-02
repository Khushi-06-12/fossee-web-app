import pandas as pd
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from .models import Dataset, Equipment
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_csv(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.FILES['file']
    
    try:
        df = pd.read_csv(csv_file)
        
        required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return Response({
                'error': f'Missing required columns: {", ".join(missing_columns)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        dataset_name = csv_file.name
        dataset = Dataset.objects.create(name=dataset_name)
        
        equipment_list = []
        for _, row in df.iterrows():
            equipment = Equipment.objects.create(
                dataset=dataset,
                equipment_name=row['Equipment Name'],
                equipment_type=row['Type'],
                flowrate=float(row['Flowrate']),
                pressure=float(row['Pressure']),
                temperature=float(row['Temperature'])
            )
            equipment_list.append({
                'id': equipment.id,
                'equipment_name': equipment.equipment_name,
                'equipment_type': equipment.equipment_type,
                'flowrate': equipment.flowrate,
                'pressure': equipment.pressure,
                'temperature': equipment.temperature
            })
        
        datasets = Dataset.objects.all().order_by('-uploaded_at')
        if datasets.count() > 5:
            for ds in datasets[5:]:
                ds.delete()
        
        return Response({
            'message': 'CSV uploaded successfully',
            'dataset_id': dataset.id,
            'dataset_name': dataset.name,
            'uploaded_at': dataset.uploaded_at,
            'equipment_count': len(equipment_list),
            'equipment': equipment_list
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'error': f'Error processing CSV: {str(e)}'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_summary(request, dataset_id):
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        equipment_list = Equipment.objects.filter(dataset=dataset)
        
        if not equipment_list.exists():
            return Response({'error': 'No equipment data found'}, status=status.HTTP_404_NOT_FOUND)
        
        total_count = equipment_list.count()
        avg_flowrate = equipment_list.aggregate(Avg('flowrate'))['flowrate__avg']
        avg_pressure = equipment_list.aggregate(Avg('pressure'))['pressure__avg']
        avg_temperature = equipment_list.aggregate(Avg('temperature'))['temperature__avg']
        
        type_distribution = {}
        for equipment in equipment_list:
            eq_type = equipment.equipment_type
            type_distribution[eq_type] = type_distribution.get(eq_type, 0) + 1
        
        return Response({
            'dataset_id': dataset.id,
            'dataset_name': dataset.name,
            'uploaded_at': dataset.uploaded_at,
            'summary': {
                'total_count': total_count,
                'averages': {
                    'flowrate': round(avg_flowrate, 2) if avg_flowrate else 0,
                    'pressure': round(avg_pressure, 2) if avg_pressure else 0,
                    'temperature': round(avg_temperature, 2) if avg_temperature else 0
                },
                'type_distribution': type_distribution
            }
        }, status=status.HTTP_200_OK)
        
    except Dataset.DoesNotExist:
        return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    datasets = Dataset.objects.all().order_by('-uploaded_at')[:5]
    
    history = []
    for dataset in datasets:
        equipment_count = Equipment.objects.filter(dataset=dataset).count()
        history.append({
            'id': dataset.id,
            'name': dataset.name,
            'uploaded_at': dataset.uploaded_at,
            'equipment_count': equipment_count
        })
    
    return Response({'history': history}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_equipment_data(request, dataset_id):
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        equipment_list = Equipment.objects.filter(dataset=dataset)
        
        data = []
        for equipment in equipment_list:
            data.append({
                'id': equipment.id,
                'equipment_name': equipment.equipment_name,
                'equipment_type': equipment.equipment_type,
                'flowrate': equipment.flowrate,
                'pressure': equipment.pressure,
                'temperature': equipment.temperature
            })
        
        return Response({'data': data}, status=status.HTTP_200_OK)
        
    except Dataset.DoesNotExist:
        return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generate_pdf(request, dataset_id):
    try:
        dataset = Dataset.objects.get(id=dataset_id)
        equipment_list = Equipment.objects.filter(dataset=dataset)
        
        if not equipment_list.exists():
            return Response({'error': 'No equipment data found'}, status=status.HTTP_404_NOT_FOUND)
        
        total_count = equipment_list.count()
        avg_flowrate = equipment_list.aggregate(Avg('flowrate'))['flowrate__avg']
        avg_pressure = equipment_list.aggregate(Avg('pressure'))['pressure__avg']
        avg_temperature = equipment_list.aggregate(Avg('temperature'))['temperature__avg']
        
        type_distribution = {}
        for equipment in equipment_list:
            eq_type = equipment.equipment_type
            type_distribution[eq_type] = type_distribution.get(eq_type, 0) + 1
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        title = Paragraph(f"Equipment Analysis Report: {dataset.name}", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Summary Statistics", styles['Heading2']))
        summary_data = [
            ['Metric', 'Value'],
            ['Total Equipment Count', str(total_count)],
            ['Average Flowrate', f"{avg_flowrate:.2f}"],
            ['Average Pressure', f"{avg_pressure:.2f}"],
            ['Average Temperature', f"{avg_temperature:.2f}"]
        ]
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Equipment Type Distribution", styles['Heading2']))
        type_data = [['Equipment Type', 'Count']]
        for eq_type, count in type_distribution.items():
            type_data.append([eq_type, str(count)])
        
        type_table = Table(type_data)
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(type_table)
        story.append(Spacer(1, 0.3*inch))
        
        story.append(Paragraph("Equipment Details", styles['Heading2']))
        equipment_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        for equipment in equipment_list[:50]:
            equipment_data.append([
                equipment.equipment_name,
                equipment.equipment_type,
                f"{equipment.flowrate:.2f}",
                f"{equipment.pressure:.2f}",
                f"{equipment.temperature:.2f}"
            ])
        
        equipment_table = Table(equipment_data)
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(equipment_table)
        
        doc.build(story)
        buffer.seek(0)
        
        response = HttpResponse(buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="equipment_report_{dataset_id}.pdf"'
        return response
        
    except Dataset.DoesNotExist:
        return Response({'error': 'Dataset not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
