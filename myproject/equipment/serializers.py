from rest_framework import serializers
from .models import Dataset, Equipment


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = '__all__'


class DatasetSerializer(serializers.ModelSerializer):
    equipments = EquipmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dataset
        fields = '__all__'
