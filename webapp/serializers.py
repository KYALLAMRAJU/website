from rest_framework import serializers
from webapp.models import *

def multiples_of_10(value): #our custom validator function (i.e independent function)
    print("inside custom validator")
    if len(value) != 0:
        raise serializers.ValidationError("The value must be a 10 digit number")

# class wishserializer(serializers.Serializer):
#     username = serializers.CharField(max_length=20)
#     name = serializers.CharField(max_length=20)
#     astrology_message = serializers.CharField(max_length=500)
#     mobilenumber = serializers.CharField(validators=[multiples_of_10]) #adding our custom validator to the mobilenumber field
#
#     def validate(self,data):
#         print("inside object level validation")
#         username=data.get('name')
#         if username.lower()=='admin':
#             raise serializers.ValidationError("username cannot be admin")
#         name=data.get('name')
#         if len(name)<4:
#             raise serializers.ValidationError("name must be at least 4 characters long")
#         return data
#
#     def create(self, validated_data): #overriding the create method to create a new wishdata object in the database with the provided validated data which is of dictionary type and of keyword variables
#         return wishdata.objects.create(**validated_data)
#
#     def update(self,instance, validated_data): #overriding the update method to update an existing wishdata object in the database with the provided validated data which is of dictionary type and of keyword variables
#         instance.username = validated_data.get('username', instance.username)
#         instance.name = validated_data.get('name', instance.name)
#         instance.astrology_message = validated_data.get('astrology_message', instance.astrology_message)
#         instance.mobilenumber = validated_data.get('mobilenumber', instance.mobilenumber)
#         instance.save()
#         return instance

class wishserializer(serializers.ModelSerializer):

    class Meta:
        model = wishdata
        fields = '__all__'

    username = serializers.CharField(max_length=20) # we can also add custom validators to the model serializer fields
    name = serializers.CharField(max_length=20)

    def validate(self,data):
        print("inside object level validation")
        username = data.get('name')
        if username is not None:
            if username.lower()=='admin':
                raise serializers.ValidationError("username cannot be admin")
        if wishdata.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError("username already exists")
        name=data.get('name')
        if name is not None:
            if len(name)<4:
                raise serializers.ValidationError("name must be at least 4 characters long")
        return data


class bookSerializer(serializers.ModelSerializer):
    class Meta:
        model = book
        fields = '__all__'


class authorSerializer(serializers.ModelSerializer):
    class Meta:
        model = author
        fields = '__all__'
    books_by_author = bookSerializer(many=True, read_only=True)


