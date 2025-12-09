"""
Homework generator for 10-Minute Reading App (V1).

Generates reading texts and writing templates from hard-coded content.
No LLM or external API required.
"""

import random
from datetime import datetime
from pathlib import Path
from typing import Tuple

from config import GENERATED_FOLDER, STUDENT_NAME
from models import GeneratedHomework


# =============================================================================
# READING TEXT BANK (V1: Hard-coded samples)
# =============================================================================

READING_TEXTS = [
    # Text 1: Ancient Egypt
    """The Land of Ancient Egypt

Ancient Egypt was one of the greatest civilizations in history. It grew along the banks of the Nile River in Africa. The Nile flooded every year, leaving behind rich soil that was perfect for farming.

The ancient Egyptians built amazing structures that still stand today. The Great Pyramid of Giza is the most famous. It was built as a tomb for the pharaoh Khufu over 4,500 years ago. The pyramid contains over two million stone blocks.

Egyptian society was organized into different groups. At the top was the pharaoh, who was believed to be a living god. Below were priests, nobles, and scribes. Most people were farmers who worked the land.

The Egyptians invented many things we still use today. They created one of the first writing systems, called hieroglyphics. They also developed a 365-day calendar and made advances in medicine and mathematics.

Life in ancient Egypt centered around religion. Egyptians believed in many gods and prepared carefully for the afterlife. This is why they preserved bodies as mummies and filled tombs with treasures.""",

    # Text 2: The Ocean
    """Life in the Ocean

The ocean covers more than 70 percent of Earth's surface. It is home to millions of different species, from tiny plankton to the enormous blue whale. Scientists believe there are still many ocean creatures we have not yet discovered.

The ocean is divided into different zones based on depth. The sunlight zone is the top layer where most sea life lives. Sunlight can reach this area, allowing plants and algae to grow. Fish, dolphins, and sea turtles swim in these waters.

Below the sunlight zone is the twilight zone. Less light reaches here, and the water is colder. Strange creatures live in this dim world, including jellyfish that glow in the dark.

The deepest part of the ocean is called the midnight zone. No sunlight reaches this area at all. The pressure is crushing, and the temperature is near freezing. Yet life still exists here. Some fish create their own light to find food.

Humans have explored only a small part of the deep ocean. Special submarines called submersibles can dive down to study these mysterious depths. Each expedition discovers something new and amazing.""",

    # Text 3: The Solar System
    """Our Solar System

Our solar system is our neighborhood in space. At its center is the Sun, a star that provides light and heat to everything around it. Eight planets orbit the Sun, each one different from the others.

Mercury is the closest planet to the Sun. It is small and covered with craters. Venus comes next and is the hottest planet because of its thick atmosphere. Earth is the third planet and the only one known to have life.

Mars is called the Red Planet because of its rusty-colored soil. Scientists have sent robots called rovers to explore its surface. Beyond Mars lies the asteroid belt, a ring of rocky objects.

The outer planets are much larger. Jupiter is the biggest planet in our solar system. It has a famous storm called the Great Red Spot. Saturn is known for its beautiful rings made of ice and rock.

Uranus and Neptune are the farthest planets. Both are made mostly of gas and are extremely cold. It takes Neptune 165 years to orbit the Sun just once. Our solar system is vast, but it is just a tiny part of the Milky Way galaxy.""",

    # Text 4: The Rainforest
    """The Amazon Rainforest

The Amazon rainforest is the largest tropical rainforest on Earth. It covers parts of nine countries in South America, with most of it in Brazil. The Amazon is sometimes called the "lungs of the Earth" because it produces so much oxygen.

The rainforest has several layers, like a tall building. The forest floor is dark because very little sunlight reaches it. Above is the understory, where small trees and shrubs grow. The canopy is the main layer, formed by the tops of tall trees.

An incredible variety of animals live in the Amazon. Colorful parrots and toucans fly through the trees. Monkeys swing from branch to branch looking for fruit. On the ground, jaguars hunt for prey, while poison dart frogs display their bright colors.

The Amazon River flows through the rainforest. It is the second longest river in the world and contains more water than any other river. Pink river dolphins swim in its waters, along with piranhas and giant catfish.

Many indigenous peoples have lived in the Amazon for thousands of years. They know how to use plants for medicine and food. Today, the rainforest faces threats from logging and farming, which destroy trees and animal habitats.""",

    # Text 5: Volcanoes
    """Understanding Volcanoes

A volcano is an opening in Earth's surface where hot melted rock can escape. This melted rock is called magma when it is underground and lava when it reaches the surface. Volcanoes can be found on every continent and even under the ocean.

Volcanoes form because Earth's outer layer is broken into large pieces called tectonic plates. These plates float on hot, liquid rock deep underground. Where plates meet or pull apart, magma can rise to the surface and create volcanoes.

There are three main types of volcanoes. Shield volcanoes are wide and gently sloping, formed by flowing lava. Cinder cone volcanoes are smaller and steeper. Stratovolcanoes are the tallest and most dangerous, built from layers of lava and ash.

When a volcano erupts, it can be very destructive. Lava flows can burn everything in their path. Ash clouds can block sunlight and make it hard to breathe. Mudflows called lahars can bury whole villages.

Despite the dangers, millions of people live near volcanoes. The soil around volcanoes is very fertile, which is good for farming. Scientists called volcanologists study volcanoes and try to predict when they might erupt, helping to keep people safe.""",
]


# =============================================================================
# WRITING TEMPLATES (V1: Hard-coded prompts)
# =============================================================================

WRITING_TEMPLATES = [
    # Template 1
    [
        "The text was mainly about...",
        "One important fact I learned is...",
        "I think this topic is interesting because...",
    ],
    
    # Template 2
    [
        "The main idea of this passage is...",
        "The author explains that...",
        "After reading this, I wonder...",
    ],
    
    # Template 3
    [
        "This text teaches us about...",
        "One example from the text is...",
        "In my opinion, the most surprising thing was...",
    ],
    
    # Template 4
    [
        "According to the text,...",
        "This is important because...",
        "I would like to learn more about...",
    ],
    
    # Template 5
    [
        "The passage describes...",
        "One detail that stood out to me is...",
        "This connects to what I already knew because...",
    ],
]


# =============================================================================
# GENERATOR CLASS
# =============================================================================

class HomeworkGenerator:
    """Generates homework assignments."""
    
    def __init__(self, output_folder: Path = GENERATED_FOLDER):
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self._used_texts = set()  # Track which texts we've used recently
    
    def generate(self, hw_number: int) -> GeneratedHomework:
        """
        Generate a new homework assignment.
        
        Args:
            hw_number: The homework number to generate
        
        Returns:
            GeneratedHomework object with file paths
        """
        # Select reading text (avoid repeating recently used)
        reading_text = self._select_reading_text()
        
        # Select writing template
        writing_prompts = self._select_writing_template()
        
        # Create files
        date_str = datetime.now().strftime("%Y%m%d")
        
        reading_filename = f"{date_str}_{STUDENT_NAME}_hw{hw_number:02d}_reading.txt"
        writing_filename = f"{date_str}_{STUDENT_NAME}_hw{hw_number:02d}_writing.txt"
        
        reading_path = self.output_folder / reading_filename
        writing_path = self.output_folder / writing_filename
        
        # Write reading file
        self._write_reading_file(reading_path, reading_text, hw_number)
        
        # Write writing file
        prompts_text = self._write_writing_file(writing_path, writing_prompts, hw_number)
        
        # Create and return the record
        return GeneratedHomework(
            hw_number=hw_number,
            reading_file=str(reading_path),
            writing_file=str(writing_path),
            reading_text=reading_text,
            writing_prompts=prompts_text,
        )
    
    def _select_reading_text(self) -> str:
        """Select a reading text, avoiding recent repeats."""
        available = [
            (i, text) for i, text in enumerate(READING_TEXTS)
            if i not in self._used_texts
        ]
        
        # If all texts used, reset
        if not available:
            self._used_texts.clear()
            available = list(enumerate(READING_TEXTS))
        
        idx, text = random.choice(available)
        self._used_texts.add(idx)
        
        return text
    
    def _select_writing_template(self) -> list:
        """Select a writing template."""
        return random.choice(WRITING_TEMPLATES)
    
    def _write_reading_file(self, path: Path, text: str, hw_number: int) -> None:
        """Write the reading file."""
        content = f"""HOMEWORK {hw_number} - READING
{'=' * 50}

Student: {STUDENT_NAME}
Date: {datetime.now().strftime('%Y-%m-%d')}

Instructions:
- Read the passage below carefully.
- Take about 10 minutes to read and understand it.
- Think about the main ideas and important details.
- Then complete the writing task.

{'=' * 50}

{text}

{'=' * 50}
End of reading passage.
"""
        path.write_text(content, encoding="utf-8")
    
    def _write_writing_file(self, path: Path, prompts: list, hw_number: int) -> str:
        """Write the writing template file. Returns the prompts as text."""
        prompts_text = "\n\n".join(
            f"{i}. {prompt}\n   ____________________________________________\n   ____________________________________________\n   ____________________________________________"
            for i, prompt in enumerate(prompts, 1)
        )
        
        content = f"""HOMEWORK {hw_number} - WRITING
{'=' * 50}

Student: {STUDENT_NAME}
Date: {datetime.now().strftime('%Y-%m-%d')}

Instructions:
- Complete each sentence starter below.
- Write at least 2-3 sentences for each prompt.
- Take about 10 minutes to complete.
- Save this file when you're done.

{'=' * 50}

{prompts_text}

{'=' * 50}

When finished, save this file as:
{datetime.now().strftime('%Y%m%d')}_{STUDENT_NAME}_hw{hw_number:02d}.txt

(or .docx if you prefer)
"""
        path.write_text(content, encoding="utf-8")
        return prompts_text


def generate_next_homework(hw_number: int) -> Tuple[Path, Path]:
    """
    Convenience function to generate the next homework.
    
    Args:
        hw_number: Homework number to generate
    
    Returns:
        Tuple of (reading_path, writing_path)
    """
    generator = HomeworkGenerator()
    result = generator.generate(hw_number)
    return Path(result.reading_file), Path(result.writing_file)
