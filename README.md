<<<<<<< HEAD
# Advancing-Aviation-Safety
=======


## then to activate the enivironment 
aviation_venv\Scripts\activate   

## install requirements
pip install -r requirements.txt 

## create a database 
CREATE DATABASE aviation_monitoring_db; (if not created)


## migarte
python manage.py makemigrations
python manage.py migrate

## train model  
python analytics\fast_ml_training.py

## createsuperuser
python manage.py createsuperuser (if not created)

## runserver

python manage.py runserver

admin is user id and password 

### to perform monitoring 
you must go to devices and alot three available models then only the users can use
those are: ecg,eeg and eye tracker
>>>>>>> 7b005ef7 (first commit)
