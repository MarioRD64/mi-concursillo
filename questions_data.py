"""
Enhanced question database for El Concursillo
Progressive difficulty levels 1-15 with multiple languages
Categories: General, Sports, Entertainment, Science, History, Geography
"""

QUESTIONS_DATABASE = {
    'es': [
        # Level 1 - €100
        {
            'text': '¿Cuál es la capital de España?',
            'options': {'A': 'Barcelona', 'B': 'Madrid', 'C': 'Sevilla', 'D': 'Valencia'},
            'correct_answer': 'B',
            'difficulty_level': 1,
            'category': 'Geografía'
        },
        {
            'text': '¿Cuántos días tiene una semana?',
            'options': {'A': '5', 'B': '6', 'C': '7', 'D': '8'},
            'correct_answer': 'C',
            'difficulty_level': 1,
            'category': 'General'
        },
        
        # Level 2 - €200
        {
            'text': '¿En qué año llegó el hombre a la Luna?',
            'options': {'A': '1967', 'B': '1969', 'C': '1971', 'D': '1973'},
            'correct_answer': 'B',
            'difficulty_level': 2,
            'category': 'Historia'
        },
        {
            'text': '¿Cuál es el planeta más cercano al Sol?',
            'options': {'A': 'Venus', 'B': 'Tierra', 'C': 'Mercurio', 'D': 'Marte'},
            'correct_answer': 'C',
            'difficulty_level': 2,
            'category': 'Ciencia'
        },
        
        # Level 3 - €300
        {
            'text': '¿Quién pintó "La Gioconda"?',
            'options': {'A': 'Picasso', 'B': 'Van Gogh', 'C': 'Da Vinci', 'D': 'Dalí'},
            'correct_answer': 'C',
            'difficulty_level': 3,
            'category': 'Arte'
        },
        {
            'text': '¿Cuál es el río más largo del mundo?',
            'options': {'A': 'Amazonas', 'B': 'Nilo', 'C': 'Yangtsé', 'D': 'Misisipi'},
            'correct_answer': 'B',
            'difficulty_level': 3,
            'category': 'Geografía'
        },
        
        # Level 4 - €500
        {
            'text': '¿En qué año se fundó YouTube?',
            'options': {'A': '2004', 'B': '2005', 'C': '2006', 'D': '2007'},
            'correct_answer': 'B',
            'difficulty_level': 4,
            'category': 'Tecnología'
        },
        
        # Level 5 - €1,000 (Safe Level)
        {
            'text': '¿Cuál es el elemento químico con símbolo "Au"?',
            'options': {'A': 'Plata', 'B': 'Oro', 'C': 'Aluminio', 'D': 'Hierro'},
            'correct_answer': 'B',
            'difficulty_level': 5,
            'category': 'Ciencia'
        },
        
        # Level 6 - €2,000
        {
            'text': '¿Quién escribió "Cien años de soledad"?',
            'options': {'A': 'Mario Vargas Llosa', 'B': 'Gabriel García Márquez', 'C': 'Jorge Luis Borges', 'D': 'Octavio Paz'},
            'correct_answer': 'B',
            'difficulty_level': 6,
            'category': 'Literatura'
        },
        
        # Level 7 - €4,000
        {
            'text': '¿Cuál es la montaña más alta del mundo?',
            'options': {'A': 'K2', 'B': 'Kangchenjunga', 'C': 'Everest', 'D': 'Lhotse'},
            'correct_answer': 'C',
            'difficulty_level': 7,
            'category': 'Geografía'
        },
        
        # Level 8 - €8,000
        {
            'text': '¿En qué año cayó el Muro de Berlín?',
            'options': {'A': '1987', 'B': '1989', 'C': '1991', 'D': '1993'},
            'correct_answer': 'B',
            'difficulty_level': 8,
            'category': 'Historia'
        },
        
        # Level 9 - €16,000
        {
            'text': '¿Cuál es la velocidad de la luz en el vacío?',
            'options': {'A': '299,792,458 m/s', 'B': '300,000,000 m/s', 'C': '299,000,000 m/s', 'D': '298,792,458 m/s'},
            'correct_answer': 'A',
            'difficulty_level': 9,
            'category': 'Física'
        },
        
        # Level 10 - €32,000 (Safe Level)
        {
            'text': '¿Quién compuso "Las Cuatro Estaciones"?',
            'options': {'A': 'Bach', 'B': 'Mozart', 'C': 'Vivaldi', 'D': 'Beethoven'},
            'correct_answer': 'C',
            'difficulty_level': 10,
            'category': 'Música'
        },
        
        # Level 11 - €64,000
        {
            'text': '¿Cuál es el hueso más largo del cuerpo humano?',
            'options': {'A': 'Húmero', 'B': 'Tibia', 'C': 'Fémur', 'D': 'Radio'},
            'correct_answer': 'C',
            'difficulty_level': 11,
            'category': 'Anatomía'
        },
        
        # Level 12 - €125,000
        {
            'text': '¿En qué año se firmó el Tratado de Versalles?',
            'options': {'A': '1918', 'B': '1919', 'C': '1920', 'D': '1921'},
            'correct_answer': 'B',
            'difficulty_level': 12,
            'category': 'Historia'
        },
        
        # Level 13 - €250,000
        {
            'text': '¿Cuál es la constante de Planck aproximadamente?',
            'options': {'A': '6.626 × 10⁻³⁴ J·s', 'B': '6.626 × 10⁻³³ J·s', 'C': '6.626 × 10⁻³⁵ J·s', 'D': '6.626 × 10⁻³² J·s'},
            'correct_answer': 'A',
            'difficulty_level': 13,
            'category': 'Física'
        },
        
        # Level 14 - €500,000
        {
            'text': '¿Cuál fue la primera novela de Cervantes?',
            'options': {'A': 'Don Quijote', 'B': 'La Galatea', 'C': 'Novelas Ejemplares', 'D': 'Los trabajos de Persiles'},
            'correct_answer': 'B',
            'difficulty_level': 14,
            'category': 'Literatura'
        },
        
        # Level 15 - €1,000,000
        {
            'text': '¿Cuál es el nombre del teorema que establece que en un triángulo rectángulo, el cuadrado de la hipotenusa es igual a la suma de los cuadrados de los catetos?',
            'options': {'A': 'Teorema de Tales', 'B': 'Teorema de Pitágoras', 'C': 'Teorema de Fermat', 'D': 'Teorema de Euclides'},
            'correct_answer': 'B',
            'difficulty_level': 15,
            'category': 'Matemáticas'
        }
    ],
    
    'en': [
        # Level 1 - €100
        {
            'text': 'What is the capital of the United Kingdom?',
            'options': {'A': 'Manchester', 'B': 'London', 'C': 'Birmingham', 'D': 'Liverpool'},
            'correct_answer': 'B',
            'difficulty_level': 1,
            'category': 'Geography'
        },
        {
            'text': 'How many continents are there?',
            'options': {'A': '5', 'B': '6', 'C': '7', 'D': '8'},
            'correct_answer': 'C',
            'difficulty_level': 1,
            'category': 'General'
        },
        
        # Level 2 - €200
        {
            'text': 'Who wrote "Romeo and Juliet"?',
            'options': {'A': 'Charles Dickens', 'B': 'William Shakespeare', 'C': 'Jane Austen', 'D': 'Mark Twain'},
            'correct_answer': 'B',
            'difficulty_level': 2,
            'category': 'Literature'
        },
        
        # Level 3 - €300
        {
            'text': 'What is the largest ocean on Earth?',
            'options': {'A': 'Atlantic', 'B': 'Indian', 'C': 'Arctic', 'D': 'Pacific'},
            'correct_answer': 'D',
            'difficulty_level': 3,
            'category': 'Geography'
        },
        
        # Level 4 - €500
        {
            'text': 'In which year did World War II end?',
            'options': {'A': '1944', 'B': '1945', 'C': '1946', 'D': '1947'},
            'correct_answer': 'B',
            'difficulty_level': 4,
            'category': 'History'
        },
        
        # Level 5 - €1,000
        {
            'text': 'What is the chemical symbol for gold?',
            'options': {'A': 'Go', 'B': 'Gd', 'C': 'Au', 'D': 'Ag'},
            'correct_answer': 'C',
            'difficulty_level': 5,
            'category': 'Science'
        }
    ],
    
    'fr': [
        # Level 1 - €100
        {
            'text': 'Quelle est la capitale de la France?',
            'options': {'A': 'Lyon', 'B': 'Marseille', 'C': 'Paris', 'D': 'Toulouse'},
            'correct_answer': 'C',
            'difficulty_level': 1,
            'category': 'Géographie'
        },
        {
            'text': 'Combien de côtés a un triangle?',
            'options': {'A': '2', 'B': '3', 'C': '4', 'D': '5'},
            'correct_answer': 'B',
            'difficulty_level': 1,
            'category': 'Général'
        },
        
        # Level 2 - €200
        {
            'text': 'Qui a écrit "Les Misérables"?',
            'options': {'A': 'Victor Hugo', 'B': 'Émile Zola', 'C': 'Gustave Flaubert', 'D': 'Marcel Proust'},
            'correct_answer': 'A',
            'difficulty_level': 2,
            'category': 'Littérature'
        }
    ],
    
    'de': [
        # Level 1 - €100
        {
            'text': 'Was ist die Hauptstadt von Deutschland?',
            'options': {'A': 'München', 'B': 'Hamburg', 'C': 'Berlin', 'D': 'Köln'},
            'correct_answer': 'C',
            'difficulty_level': 1,
            'category': 'Geographie'
        },
        {
            'text': 'Wie viele Beine hat eine Spinne?',
            'options': {'A': '6', 'B': '8', 'C': '10', 'D': '12'},
            'correct_answer': 'B',
            'difficulty_level': 1,
            'category': 'Allgemein'
        }
    ]
}
