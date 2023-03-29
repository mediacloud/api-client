import os.path
import logging
from dotenv import load_dotenv


TEST_USER_EMAIL = "mc-api-test@media.mit.edu"

QUERY_LAST_FEW_DAYS = "publish_date:[NOW-3DAY TO NOW]"
QUERY_LAST_WEEK = "publish_date:[NOW-7DAY TO NOW]"
QUERY_LAST_MONTH = "publish_date:[NOW-31DAY TO NOW]"
QUERY_LAST_YEAR = "publish_date:[NOW-1YEAR TO NOW]"
QUERY_LAST_DECADE = "publish_date:[NOW-10YEAR TO NOW]"
QUERY_ENGLISH_LANGUAGE = "language:en"

# useful for testing very long queries that need to be sent as POST
LONG_ENGLISH_QUERY = '((Scien* OR research* OR study OR studies) OR (Tech* OR Google OR Facebook OR Alphabet OR Amazon OR Netflix OR Twitter OR Instagram OR "consumer tech*" OR Snapchat OR WhatsApp OR SpaceX OR Tesla) OR (weather OR forecast OR flood OR storm OR hurricane OR typhoon OR cyclone OR "heat wave" OR tornado OR blizzard OR avalanche OR drought OR landslide OR mudslide OR wildfire OR lightning OR (climate AND NOT "political climate")) OR (health OR disease OR ill* OR medic* OR deaths) OR (business* OR financ* OR stock OR econom* OR bank OR invest* OR "wall street" OR recession OR "bull market" OR "bear market" OR inflation OR IPO OR "hedge fund" OR "mutual fund" OR broker) OR (sport* OR baseball OR basketball OR football OR soccer OR hockey OR tennis OR golf OR boxing OR mma OR "mixed martial arts" OR NASCAR OR "car racing" OR Olympi* OR ski* OR snowboard*  OR swim* OR gymnast*) OR (art OR arts OR celeb* OR movie* OR television OR music* OR "pop culture" OR books OR tv OR theater OR theatre OR gaming) OR (Trump OR Obama OR Democrat* OR Republican* OR Senat* OR Representative  OR "First Lady" OR Governor OR campaign OR election) OR ("Afghanistan" OR "Albania" OR "Algeria" OR "Andorra" OR "Angola" OR "Antigua and Barbuda" OR "Argentina" OR "Armenia" OR "Australia" OR "Austria" OR "Azerbaijan" OR "Bahamas" OR "Bahrain" OR "Bangladesh" OR "Barbados" OR "Belarus" OR "Belgium" OR "Belize" OR "Benin" OR "Bhutan" OR "Bolivia" OR "Bosnia and Herzegovina" OR "Botswana" OR "Brazil" OR "Brunei" OR "Bulgaria" OR "Burkina Faso" OR "Burundi" OR "Cabo Verde" OR "Cambodia" OR "Cameroon" OR "Canada" OR "Central African Republic" OR "Chad" OR "Chile" OR "China" OR "Colombia" OR "Comoros" OR "Congo" OR "Costa Rica" OR "Ivory Coast" OR "Croatia" OR "Cuba" OR "Cyprus" OR "Czech Republic" OR "Denmark" OR "Djibouti" OR "Dominica" OR "Dominican Republic" OR "East Timor (Timor-Leste)" OR "Ecuador" OR "Egypt" OR "El Salvador" OR "Equatorial Guinea" OR "Eritrea" OR "Estonia" OR "Eswatini" OR "Swaziland" OR "Ethiopia" OR "Fiji" OR "Finland" OR "France" OR "Gabon" OR "The Gambia" OR "Georgia" OR "Germany" OR "Ghana" OR "Greece" OR "Grenada" OR "Guatemala" OR "Guinea" OR "Guinea-Bissau" OR "Guyana" OR "Haiti" OR "Honduras" OR "Hungary" OR "Iceland" OR "India" OR "Indonesia" OR "Iran" OR "Iraq" OR "Ireland" OR "Israel" OR "Italy" OR "Jamaica" OR "Japan" OR "Kazakhstan" OR "Kenya" OR "Kiribati" OR "North Korea" OR "South Korea" OR "Kosovo" OR "Kuwait" OR "Kyrgyzstan" OR "Laos" OR "Latvia" OR "Lebanon" OR "Lesotho" OR "Liberia" OR "Libya" OR "Liechtenstein" OR "Lithuania" OR "Luxembourg" OR "Madagascar" OR "Malawi" OR "Malaysia" OR "Maldives" OR "Mali" OR "Malta" OR "Marshall Islands" OR "Mauritania" OR "Mauritius" OR "Mexico" OR "Micronesia, Federated States of" OR "Moldova" OR "Monaco" OR "Mongolia" OR "Montenegro" OR "Morocco" OR "Mozambique" OR "Myanmar " OR "Burma" OR "Namibia" OR "Nauru" OR "Nepal" OR "Netherlands" OR "New Zealand" OR "Nicaragua" OR "Niger" OR "Nigeria" OR "North Macedonia" OR "Norway" OR "Oman" OR "Pakistan" OR "Palau" OR "Panama" OR "Papua New Guinea" OR "Paraguay" OR "Peru" OR "Philippines" OR "Poland" OR "Portugal" OR "Qatar" OR "Romania" OR "Russia" OR "Rwanda" OR "Saint Kitts and Nevis" OR "Saint Lucia" OR "Saint Vincent and the Grenadines" OR "Samoa" OR "San Marino" OR "Sao Tome and Principe" OR "Saudi Arabia" OR "Senegal" OR "Serbia" OR "Seychelles" OR "Sierra Leone" OR "Singapore" OR "Slovakia" OR "Slovenia" OR "Solomon Islands" OR "Somalia" OR "South Africa" OR "Spain" OR "Sri Lanka" OR "Sudan" OR "South Sudan" OR "Suriname" OR "Sweden" OR "Switzerland" OR "Syria" OR "Taiwan" OR "Tajikistan" OR "Tanzania" OR "Thailand" OR "Togo" OR "Tonga" OR "Trinidad and Tobago" OR "Tunisia" OR "Turkey" OR "Turkmenistan" OR "Tuvalu" OR "Uganda" OR "Ukraine" OR "United Arab Emirates" OR "United Kingdom" OR "Uruguay" OR "Uzbekistan" OR "Vanuatu" OR "Vatican City" OR "Venezuela" OR "Vietnam" OR "Yemen" OR "Zambia" OR "Zimbabwe" OR "Timor Leste"))'

basedir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

logger = logging.getLogger(__name__)

# load env-vars from .env file if there is one
test_env = os.path.join(basedir, '.env')
if os.path.isfile(test_env):
    load_dotenv(dotenv_path=os.path.join(basedir, '.env'), verbose=True)


def load_text_from_fixture(filename):
    with open(os.path.join(basedir, "mediacloud", "test", "fixtures", filename), 'r') as f:
        text = f.read()
    return text
