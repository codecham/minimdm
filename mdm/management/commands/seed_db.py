import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mdm.models import Fleet, Device


class Command(BaseCommand):
    help = 'Seed the database with sample data from JSON file (clears existing data)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        # Load JSON data first (to validate before asking confirmation)
        json_path = Path(__file__).resolve().parent.parent.parent / 'fixtures' / 'seed_data.json'
        
        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'\n❌ File not found: {json_path}\n'))
            return
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Invalid JSON file: {e}\n'))
            return
        
        # Validate data
        errors = self.validate_data(data)
        if errors:
            self.stdout.write(self.style.ERROR('\n❌ Validation errors found:\n'))
            for error in errors:
                self.stdout.write(self.style.ERROR(f'  • {error}'))
            self.stdout.write('')
            return
        
        # Warning and confirmation
        if not options['no_input']:
            self.stdout.write(self.style.WARNING('\n⚠️  WARNING: This will DELETE all existing data!\n'))
            self.stdout.write('The following will be erased:')
            self.stdout.write(f'  - {User.objects.count()} users')
            self.stdout.write(f'  - {Fleet.objects.count()} fleets')
            self.stdout.write(f'  - {Device.objects.count()} devices')
            self.stdout.write('')
            
            confirm = input('Are you sure you want to continue? (yes/no): ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('\nOperation cancelled.\n'))
                return
        
        # Seed the database
        try:
            self.seed_database(data)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error while seeding: {e}\n'))
            return

    def validate_data(self, data):
        """Validate all data before seeding."""
        errors = []
        
        # Validate users
        users = data.get('users', [])
        if not users:
            errors.append('No users defined in seed_data.json')
        
        usernames = set()
        for i, user in enumerate(users):
            prefix = f'users[{i}]'
            
            # Username
            username = user.get('username', '')
            if not username:
                errors.append(f'{prefix}: username is required')
            elif len(username) < 3:
                errors.append(f'{prefix}: username must be at least 3 characters (got "{username}")')
            elif username in usernames:
                errors.append(f'{prefix}: duplicate username "{username}"')
            else:
                usernames.add(username)
            
            # Email
            email = user.get('email', '')
            if not email:
                errors.append(f'{prefix}: email is required')
            elif '@' not in email:
                errors.append(f'{prefix}: invalid email format "{email}"')
            
            # Password
            password = user.get('password', '')
            if not password:
                errors.append(f'{prefix}: password is required')
            elif len(password) < 8:
                errors.append(f'{prefix}: password must be at least 8 characters')
        
        # Validate fleets
        fleets = data.get('fleets', [])
        fleet_keys = set()  # Format: "owner:fleet_name"
        for i, fleet in enumerate(fleets):
            prefix = f'fleets[{i}]'
            
            # Name
            name = fleet.get('name', '')
            if not name:
                errors.append(f'{prefix}: name is required')
            
            # Owner
            owner = fleet.get('owner', '')
            if not owner:
                errors.append(f'{prefix}: owner is required')
            elif owner not in usernames:
                errors.append(f'{prefix}: owner "{owner}" not found in users')
            
            # Unique name per owner
            fleet_key = f"{owner}:{name}"
            if fleet_key in fleet_keys:
                errors.append(f'{prefix}: duplicate fleet name "{name}" for owner "{owner}"')
            else:
                fleet_keys.add(fleet_key)
        
        # Validate devices
        devices = data.get('devices', [])
        for i, device in enumerate(devices):
            prefix = f'devices[{i}]'
            
            # Fleet (format: "owner:fleet_name")
            fleet = device.get('fleet', '')
            if not fleet:
                errors.append(f'{prefix}: fleet is required')
            elif ':' not in fleet:
                errors.append(f'{prefix}: fleet must be in format "owner:fleet_name" (got "{fleet}")')
            elif fleet not in fleet_keys:
                errors.append(f'{prefix}: fleet "{fleet}" not found in fleets')
            
            # OS Version (optional but must be positive if provided)
            os_version = device.get('os_version')
            if os_version is not None and (not isinstance(os_version, int) or os_version < 0):
                errors.append(f'{prefix}: os_version must be a positive integer (got "{os_version}")')
        
        return errors

    def seed_database(self, data):
        """Seed the database with validated data."""
        self.stdout.write('\nSeeding database...\n')
        
        # Clear ALL existing data
        self.stdout.write('Clearing existing data...')
        Device.objects.all().delete()
        Fleet.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('  Done\n'))
        
        # Create users
        self.stdout.write('Creating users...')
        users = {}
        for user_data in data.get('users', []):
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data.get('email', ''),
                password=user_data['password'],
            )
            user.is_staff = user_data.get('is_staff', False)
            user.is_superuser = user_data.get('is_superuser', False)
            user.save()
            
            users[user.username] = user
            role = 'admin' if user.is_staff else 'user'
            self.stdout.write(self.style.SUCCESS(f'  Created [{role}]: {user.username}'))
        
        # Create fleets
        self.stdout.write('\nCreating fleets...')
        fleets = {}
        for fleet_data in data.get('fleets', []):
            owner = users[fleet_data['owner']]
            fleet = Fleet.objects.create(
                name=fleet_data['name'],
                owner=owner,
            )
            # Key format: "owner:fleet_name"
            fleets[f"{owner.username}:{fleet.name}"] = fleet
            self.stdout.write(self.style.SUCCESS(f'  Created: {fleet.name} (owner: {owner.username})'))
        
        # Create devices
        self.stdout.write('\nCreating devices...')
        for device_data in data.get('devices', []):
            # Parse "owner:fleet_name" format
            fleet_key = device_data['fleet']
            fleet = fleets[fleet_key]
            
            device = Device.objects.create(
                fleet=fleet,
                os_version=device_data.get('os_version'),
            )
            os_info = f'OS v{device.os_version}' if device.os_version else 'no OS'
            self.stdout.write(self.style.SUCCESS(f'  Created: {device.serial_number} ({os_info})'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!\n'))
        self.stdout.write('Test accounts:')
        for user_data in data.get('users', []):
            role = 'admin' if user_data.get('is_staff') else 'user'
            self.stdout.write(f'  [{role}] {user_data["username"]} / {user_data["password"]}')
        
        self.stdout.write('\nGet a token:')
        self.stdout.write('  curl -X POST http://localhost:8000/api/auth/token/ \\')
        self.stdout.write('    -H "Content-Type: application/json" \\')
        self.stdout.write('    -d \'{"username": "alice", "password": "alice123"}\'')
        self.stdout.write('')