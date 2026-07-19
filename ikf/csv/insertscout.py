python manage.py shell
import csv
from main.models import Scout
file_path = 'csv/scoutdata.csv'  # adjust if it's somewhere else

with open(file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        scout, created = Scout.objects.get_or_create(
            mobile_number=row['Mobile Number'],
            defaults={
                'ikf_id': row['Scout ID'],
                'full_name': row['Full Name'],
                'location': row['Location'],
                'preferred_cities': row['Preferred Cities where you can Scout'],
                'gmail_id': row['Gmail ID'],
                'linkedin': row['Linkedin Handle (Enter Link)'],
                'instagram': row['Instagram Handle (Enter Link)'],
                'facebook': row['Facebook Handle (Enter Link)'],
                'ikf_tshirt': row['Do you have IKF T-Shirt ?'].strip().lower() in ['yes', 'true', '1'],
                'pan_number': row['PAN Number'],
                'bank_details': row['Bank Account Details'],
            }
        )