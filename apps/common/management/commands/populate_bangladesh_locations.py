from django.core.management.base import BaseCommand
from apps.common.models import District, Thana


class Command(BaseCommand):
    help = 'Populate Bangladesh districts and thanas data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Thana.objects.all().delete()
            District.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Existing data cleared.'))

        # Bangladesh Districts and Thanas data
        districts_data = {
            'Barisal': {
                'code': 'BAR',
                'thanas': [
                    'Agailjhara', 'Babuganj', 'Bakerganj', 'Banari Para', 'Barisal Sadar',
                    'Gouranadi', 'Hizla', 'Mehendiganj', 'Muladi', 'Wazirpur'
                ]
            },
            'Barguna': {
                'code': 'BRG',
                'thanas': [
                    'Amtali', 'Bamna', 'Barguna Sadar', 'Betagi', 'Patharghata', 'Taltali'
                ]
            },
            'Bhola': {
                'code': 'BHO',
                'thanas': [
                    'Bhola Sadar', 'Burhanuddin', 'Char Fasson', 'Daulatkhan', 'Lalmohan', 'Manpura', 'Tazumuddin'
                ]
            },
            'Jhalokati': {
                'code': 'JHA',
                'thanas': [
                    'Jhalokati Sadar', 'Kathalia', 'Nalchity', 'Rajapur'
                ]
            },
            'Patuakhali': {
                'code': 'PAT',
                'thanas': [
                    'Bauphal', 'Dashmina', 'Dumki', 'Galachipa', 'Kalapara', 'Mirzaganj', 'Patuakhali Sadar', 'Rangabali'
                ]
            },
            'Pirojpur': {
                'code': 'PIR',
                'thanas': [
                    'Bhandaria', 'Kawkhali', 'Mathbaria', 'Nazirpur', 'Nesarabad', 'Pirojpur Sadar', 'Zianagar'
                ]
            },
            'Bandarban': {
                'code': 'BAN',
                'thanas': [
                    'Ali Kadam', 'Bandarban Sadar', 'Lama', 'Naikhongchhari', 'Rowangchhari', 'Ruma', 'Thanchi'
                ]
            },
            'Brahmanbaria': {
                'code': 'BRA',
                'thanas': [
                    'Akhaura', 'Bancharampur', 'Brahmanbaria Sadar', 'Kasba', 'Nabinagar', 'Nasirnagar', 'Sarail', 'Ashuganj', 'Bijoynagar'
                ]
            },
            'Chandpur': {
                'code': 'CHA',
                'thanas': [
                    'Chandpur Sadar', 'Faridganj', 'Haimchar', 'Haziganj', 'Kachua', 'Matlab Dakshin', 'Matlab Uttar', 'Shahrasti'
                ]
            },
            'Chittagong': {
                'code': 'CTG',
                'thanas': [
                    'Anowara', 'Banshkhali', 'Boalkhali', 'Chandanaish', 'Chittagong Port', 'Double Mooring', 'Fatikchhari',
                    'Hathazari', 'Kotwali', 'Lohagara', 'Mirsharai', 'Patiya', 'Rangunia', 'Raozan', 'Sandwip', 'Satkania', 'Sitakunda'
                ]
            },
            'Comilla': {
                'code': 'COM',
                'thanas': [
                    'Barura', 'Brahmanpara', 'Burichang', 'Chandina', 'Chauddagram', 'Comilla Adarsha Sadar',
                    'Comilla Sadar Dakshin', 'Daudkandi', 'Debidwar', 'Homna', 'Laksam', 'Manoharganj',
                    'Meghna', 'Monohorgonj', 'Muradnagar', 'Nangalkot', 'Titas'
                ]
            },
            'Cox\'s Bazar': {
                'code': 'COX',
                'thanas': [
                    'Chakaria', 'Cox\'s Bazar Sadar', 'Kutubdia', 'Maheshkhali', 'Pekua', 'Ramu', 'Teknaf', 'Ukhia'
                ]
            },
            'Feni': {
                'code': 'FEN',
                'thanas': [
                    'Chhagalnaiya', 'Daganbhuiyan', 'Feni Sadar', 'Fulgazi', 'Parshuram', 'Sonagazi'
                ]
            },
            'Khagrachhari': {
                'code': 'KHA',
                'thanas': [
                    'Dighinala', 'Khagrachhari Sadar', 'Lakshmichhari', 'Mahalchhari', 'Manikchhari', 'Matiranga', 'Panchhari', 'Ramgarh'
                ]
            },
            'Lakshmipur': {
                'code': 'LAK',
                'thanas': [
                    'Kamalnagar', 'Lakshmipur Sadar', 'Raipur', 'Ramganj', 'Ramgati'
                ]
            },
            'Noakhali': {
                'code': 'NOA',
                'thanas': [
                    'Begumganj', 'Chatkhil', 'Companiganj', 'Hatiya', 'Kabirhat', 'Noakhali Sadar', 'Senbagh', 'Sonaimuri', 'Subarnachar'
                ]
            },
            'Rangamati': {
                'code': 'RAN',
                'thanas': [
                    'Bagaichhari', 'Barkal', 'Kawkhali', 'Belaichhari', 'Kaptai', 'Juraichhari', 'Langadu', 'Naniyachar', 'Rajasthali', 'Rangamati Sadar'
                ]
            },
            'Dhaka': {
                'code': 'DHA',
                'thanas': [
                    'Dhamrai', 'Dohar', 'Keraniganj', 'Nawabganj', 'Savar'
                ]
            },
            'Faridpur': {
                'code': 'FAR',
                'thanas': [
                    'Alfadanga', 'Bhanga', 'Boalmari', 'Charbhadrasan', 'Faridpur Sadar', 'Madhukhali', 'Nagarkanda', 'Sadarpur', 'Saltha'
                ]
            },
            'Gazipur': {
                'code': 'GAZ',
                'thanas': [
                    'Gazipur Sadar', 'Kaliakair', 'Kaliganj', 'Kapasia', 'Sreepur'
                ]
            },
            'Gopalganj': {
                'code': 'GOP',
                'thanas': [
                    'Gopalganj Sadar', 'Kashiani', 'Kotalipara', 'Muksudpur', 'Tungipara'
                ]
            },
            'Kishoreganj': {
                'code': 'KIS',
                'thanas': [
                    'Austagram', 'Bajitpur', 'Bhairab', 'Hossainpur', 'Itna', 'Karimganj', 'Katiadi', 'Kishoreganj Sadar',
                    'Kuliarchar', 'Mithamain', 'Nikli', 'Pakundia', 'Tarail'
                ]
            },
            'Madaripur': {
                'code': 'MAD',
                'thanas': [
                    'Kalkini', 'Madaripur Sadar', 'Rajoir', 'Shibchar'
                ]
            },
            'Manikganj': {
                'code': 'MAN',
                'thanas': [
                    'Daulatpur', 'Ghior', 'Harirampur', 'Manikganj Sadar', 'Saturia', 'Shivalaya', 'Singair'
                ]
            },
            'Munshiganj': {
                'code': 'MUN',
                'thanas': [
                    'Gazaria', 'Lohajang', 'Munshiganj Sadar', 'Serajdikhan', 'Sreenagar', 'Tongibari'
                ]
            },
            'Narayanganj': {
                'code': 'NAR',
                'thanas': [
                    'Araihazar', 'Bandar', 'Narayanganj Sadar', 'Rupganj', 'Sonargaon'
                ]
            },
            'Rajbari': {
                'code': 'RJB',
                'thanas': [
                    'Baliakandi', 'Goalandaghat', 'Pangsha', 'Rajbari Sadar', 'Kalukhali'
                ]
            },
            'Shariatpur': {
                'code': 'SHA',
                'thanas': [
                    'Bhedarganj', 'Damudya', 'Gosairhat', 'Naria', 'Shariatpur Sadar', 'Zajira'
                ]
            },
            'Tangail': {
                'code': 'TAN',
                'thanas': [
                    'Basail', 'Bhuapur', 'Delduar', 'Ghatail', 'Gopalpur', 'Kalihati', 'Madhupur', 'Mirzapur',
                    'Nagarpur', 'Sakhipur', 'Tangail Sadar', 'Dhanbari'
                ]
            },
            'Bagerhat': {
                'code': 'BAG',
                'thanas': [
                    'Bagerhat Sadar', 'Chitalmari', 'Fakirhat', 'Kachua', 'Mollahat', 'Mongla', 'Morrelganj', 'Rampal', 'Sarankhola'
                ]
            },
            'Chuadanga': {
                'code': 'CHU',
                'thanas': [
                    'Alamdanga', 'Chuadanga Sadar', 'Damurhuda', 'Jibannagar'
                ]
            },
            'Jessore': {
                'code': 'JES',
                'thanas': [
                    'Abhaynagar', 'Bagherpara', 'Chaugachha', 'Jhikargachha', 'Keshabpur', 'Jessore Sadar', 'Manirampur', 'Sharsha'
                ]
            },
            'Jhenaidah': {
                'code': 'JHE',
                'thanas': [
                    'Harinakunda', 'Jhenaidah Sadar', 'Kaliganj', 'Kotchandpur', 'Maheshpur', 'Shailkupa'
                ]
            },
            'Khulna': {
                'code': 'KHU',
                'thanas': [
                    'Batiaghata', 'Dacope', 'Dumuria', 'Dighalia', 'Koyra', 'Paikgachha', 'Phultala', 'Rupsa', 'Terokhada'
                ]
            },
            'Kushtia': {
                'code': 'KUS',
                'thanas': [
                    'Bheramara', 'Daulatpur', 'Khoksa', 'Kumarkhali', 'Kushtia Sadar', 'Mirpur'
                ]
            },
            'Magura': {
                'code': 'MAG',
                'thanas': [
                    'Magura Sadar', 'Mohammadpur', 'Shalikha', 'Sreepur'
                ]
            },
            'Meherpur': {
                'code': 'MEH',
                'thanas': [
                    'Gangni', 'Meherpur Sadar', 'Mujibnagar'
                ]
            },
            'Narail': {
                'code': 'NRL',
                'thanas': [
                    'Kalia', 'Lohagara', 'Narail Sadar'
                ]
            },
            'Satkhira': {
                'code': 'SAT',
                'thanas': [
                    'Assasuni', 'Debhata', 'Kalaroa', 'Kaliganj', 'Satkhira Sadar', 'Shyamnagar', 'Tala'
                ]
            },
            'Jamalpur': {
                'code': 'JAM',
                'thanas': [
                    'Baksiganj', 'Dewanganj', 'Islampur', 'Jamalpur Sadar', 'Madarganj', 'Melandaha', 'Sarishabari'
                ]
            },
            'Mymensingh': {
                'code': 'MYM',
                'thanas': [
                    'Bhaluka', 'Dhobaura', 'Fulbaria', 'Gaffargaon', 'Gouripur', 'Haluaghat', 'Ishwarganj',
                    'Mymensingh Sadar', 'Muktagachha', 'Nandail', 'Phulpur', 'Trishal', 'Tara Khanda'
                ]
            },
            'Netrakona': {
                'code': 'NET',
                'thanas': [
                    'Atpara', 'Barhatta', 'Durgapur', 'Khaliajuri', 'Kalmakanda', 'Kendua', 'Madan', 'Mohanganj', 'Netrakona Sadar', 'Purbadhala'
                ]
            },
            'Sherpur': {
                'code': 'SHE',
                'thanas': [
                    'Jhenaigati', 'Nakla', 'Nalitabari', 'Sherpur Sadar', 'Sreebardi'
                ]
            },
            'Bogra': {
                'code': 'BOG',
                'thanas': [
                    'Adamdighi', 'Bogra Sadar', 'Dhunat', 'Dhupchanchia', 'Gabtali', 'Kahaloo', 'Nandigram',
                    'Sariakandi', 'Shajahanpur', 'Sherpur', 'Shibganj', 'Sonatola'
                ]
            },
            'Joypurhat': {
                'code': 'JOY',
                'thanas': [
                    'Akkelpur', 'Joypurhat Sadar', 'Kalai', 'Khetlal', 'Panchbibi'
                ]
            },
            'Naogaon': {
                'code': 'NAO',
                'thanas': [
                    'Atrai', 'Badalgachhi', 'Manda', 'Dhamoirhat', 'Mohadevpur', 'Naogaon Sadar', 'Niamatpur', 'Patnitala', 'Porsha', 'Raninagar', 'Sapahar'
                ]
            },
            'Natore': {
                'code': 'NAT',
                'thanas': [
                    'Bagatipara', 'Baraigram', 'Gurudaspur', 'Lalpur', 'Natore Sadar', 'Singra'
                ]
            },
            'Chapainawabganj': {
                'code': 'CWB',
                'thanas': [
                    'Bholahat', 'Gomastapur', 'Nachole', 'Chapainawabganj Sadar', 'Shibganj'
                ]
            },
            'Pabna': {
                'code': 'PAB',
                'thanas': [
                    'Atgharia', 'Bera', 'Bhangura', 'Chatmohar', 'Faridpur', 'Ishwardi', 'Pabna Sadar', 'Santhia', 'Sujanagar'
                ]
            },
            'Rajshahi': {
                'code': 'RAJ',
                'thanas': [
                    'Bagha', 'Bagmara', 'Charghat', 'Durgapur', 'Godagari', 'Mohanpur', 'Paba', 'Puthia', 'Tanore'
                ]
            },
            'Sirajganj': {
                'code': 'SIR',
                'thanas': [
                    'Belkuchi', 'Chauhali', 'Kamarkhand', 'Kazipur', 'Raiganj', 'Shahjadpur', 'Sirajganj Sadar', 'Tarash', 'Ullahpara'
                ]
            },
            'Dinajpur': {
                'code': 'DIN',
                'thanas': [
                    'Birampur', 'Birganj', 'Biral', 'Bochaganj', 'Chirirbandar', 'Dinajpur Sadar', 'Fulbari',
                    'Ghoraghat', 'Hakimpur', 'Kaharole', 'Khansama', 'Nawabganj', 'Parbatipur'
                ]
            },
            'Gaibandha': {
                'code': 'GAI',
                'thanas': [
                    'Fulchhari', 'Gaibandha Sadar', 'Gobindaganj', 'Palashbari', 'Sadullapur', 'Saghata', 'Sundarganj'
                ]
            },
            'Kurigram': {
                'code': 'KUR',
                'thanas': [
                    'Bhurungamari', 'Char Rajibpur', 'Chilmari', 'Kurigram Sadar', 'Nageshwari', 'Phulbari', 'Rajarhat', 'Raomari', 'Ulipur'
                ]
            },
            'Lalmonirhat': {
                'code': 'LAL',
                'thanas': [
                    'Aditmari', 'Hatibandha', 'Kaliganj', 'Lalmonirhat Sadar', 'Patgram'
                ]
            },
            'Nilphamari': {
                'code': 'NIL',
                'thanas': [
                    'Dimla', 'Domar', 'Jaldhaka', 'Kishoreganj', 'Nilphamari Sadar', 'Saidpur'
                ]
            },
            'Panchagarh': {
                'code': 'PAN',
                'thanas': [
                    'Atwari', 'Boda', 'Debiganj', 'Panchagarh Sadar', 'Tetulia'
                ]
            },
            'Rangpur': {
                'code': 'RNG',
                'thanas': [
                    'Badarganj', 'Gangachara', 'Kaunia', 'Rangpur Sadar', 'Mithapukur', 'Pirgachha', 'Pirganj', 'Taraganj'
                ]
            },
            'Thakurgaon': {
                'code': 'THA',
                'thanas': [
                    'Baliadangi', 'Haripur', 'Pirganj', 'Ranisankail', 'Thakurgaon Sadar'
                ]
            },
            'Habiganj': {
                'code': 'HAB',
                'thanas': [
                    'Ajmiriganj', 'Bahubal', 'Baniyachong', 'Chunarughat', 'Habiganj Sadar', 'Lakhai', 'Madhabpur', 'Nabiganj', 'Sayestaganj'
                ]
            },
            'Moulvibazar': {
                'code': 'MOU',
                'thanas': [
                    'Barlekha', 'Juri', 'Kamalganj', 'Kulaura', 'Moulvibazar Sadar', 'Rajnagar', 'Sreemangal'
                ]
            },
            'Sunamganj': {
                'code': 'SUN',
                'thanas': [
                    'Bishwamvarpur', 'Chhatak', 'Derai', 'Dharamapasha', 'Dowarabazar', 'Jagannathpur', 'Jamalganj', 'Sulla', 'Sunamganj Sadar', 'Tahirpur'
                ]
            },
            'Sylhet': {
                'code': 'SYL',
                'thanas': [
                    'Balaganj', 'Beanibazar', 'Bishwanath', 'Companigonj', 'Fenchuganj', 'Golapganj', 'Gowainghat', 'Jaintiapur', 'Kanaighat', 'Sylhet Sadar', 'Zakiganj', 'Dakshin Surma'
                ]
            }
        }

        self.stdout.write('Creating districts and thanas...')
        
        districts_created = 0
        thanas_created = 0

        for district_name, district_info in districts_data.items():
            # Create district
            district, created = District.objects.get_or_create(
                name=district_name,
                defaults={
                    'code': district_info['code'],
                    'is_active': True
                }
            )
            
            if created:
                districts_created += 1
                self.stdout.write(f'Created district: {district_name}')
            
            # Create thanas for this district
            for thana_name in district_info['thanas']:
                thana, created = Thana.objects.get_or_create(
                    name=thana_name,
                    district=district,
                    defaults={
                        'code': f"{district_info['code']}{len(district_info['thanas']):02d}",
                        'is_active': True
                    }
                )
                
                if created:
                    thanas_created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated {districts_created} districts and {thanas_created} thanas'
            )
        )
        
        # Display summary
        total_districts = District.objects.count()
        total_thanas = Thana.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Total in database: {total_districts} districts, {total_thanas} thanas'
            )
        )
