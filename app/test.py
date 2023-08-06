import spacy
from spacy.matcher import Matcher

# Load the English language model
nlp = spacy.load("en_core_web_sm")

# Create a matcher object
clothing_matcher = Matcher(nlp.vocab)

# Create a list of common clothing-related words
#clothing_related_words = ["coat", "jacket", "shirt", "pants", "jeans", "sweater", "shoes", "boots", "t-shirt", "top", "dress", "skirt", "shorts", "blouse", "hoodie", "socks", "sandals", "sneakers"]

clothing_related_words = [    "dress", "bag", "bags", "shirt", "pants", "trench coat", "trench coats", "light jackets", "denim jackets", "jacket", "jackets", "coat", "shoes", "sneakers", "boots", "heels", "blouse", "skirt", "shorts",
                      "sweater", "hoodie", "t-shirt", "jeans", "leggings", "scarf", "tie", "vest", "suit", "swimwear", "lingerie", "socks",
                      "gloves", "hat", "beanie", "cap", "belt", "watch", "earrings", "bracelet", "necklace", "ring", "backpack", "purse",
                      "sunglasses", "umbrella", "pajamas", "robe", "coatigan", "kimono", "blazer", "cardigan", "romper", "jumpsuit", "bodysuit",
                      "tank top", "crop top", "peplum top", "off-the-shoulder top", "wrap top", "tunic", "maxi dress", "midi dress", "mini dress",
                      "shift dress", "a-line dress", "fit-and-flare dress", "bodycon dress", "wrap dress", "joggers", "cargo pants", "chinos",
                      "cropped pants", "culottes", "high-waisted pants", "skinny jeans", "straight leg jeans", "bootcut jeans", "flared jeans",
                      "boyfriend jeans", "mom jeans", "denim jacket", "leather jacket", "bomber jacket", "parka", "parkas", "puffer jacket", "windbreaker",
                      "raincoat", "snow boots", "riding boots", "loafers", "mules", "sandals", "flip flops", "espadrilles", "wedges", "platforms",
                      "penny loafers", "ankle boots", "knee-high boots", "oxfords", "slip-on sneakers", "high-top sneakers", "low-top sneakers", "running shoes", "cross-training shoes"]


# Create a pattern to capture clothing items, looking for a sequence of adjectives followed by a clothing-related noun
clothing_pattern = [{"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "LOWER": {"IN": clothing_related_words}}]

# Create a pattern to capture clothing items, looking for a sequence of adjectives and noun compounds followed by a clothing-related noun
clothing_pattern2 = [{"DEP": {"IN": ["amod", "compound"]}}, {"POS": "NOUN", "LEMMA": {"IN": clothing_related_words}}]

# Add the pattern to the matcher
clothing_matcher.add("CLOTHING", [clothing_pattern, clothing_pattern2])

# Load the content of the text file
content = "For spring in New York, you'll want to dress for changeable weather, as temperatures can range from cool to warm. Here are some ideas:\n\n1. Light layers: A denim or leather jacket worn over a light sweater or tee is the perfect combo for those days when it's cool in the morning but warmer in the afternoon.\n\n2. Midi-length dresses: These versatile dresses are perfect for spring in NYC. Paired with sneakers, flats or heels and a crossbody bag, they're a chic and comfortable option for any day of the week.\n\n3. Crop tops: They're perfect for warmer days and can be dressed up or down. Paired with denim shorts, high-waisted jeans or a midi skirt, they're a fun and fresh look. chunky sneakers: Comfort is key for all-day walking around the city. You can pair chunky sneakers with dresses, jeans or shorts for a trendy sporty vibe.\n\n5. Monochrome looks: A monochrome look is a great way to stay chic while keeping things simple. Try pairing a cream oversized sweater with white jeans or a gray power suit, for example.\n\nRemember to have fun with your outfits - New York is a fashion-forward city, so don't be afraid to experiment with trends and styles."

# Create a document object from the text
doc = nlp(content)

# Find all the adjectives and nouns in the sentence
adjectives = [token.text for token in doc if token.pos_ == "ADJ"]

print("adjectives: ", adjectives)

nouns = [token.text for token in doc if token.pos_ == "NOUN"]

print("nouns: ", nouns)

# Find all matches for the clothing pattern in the document
matches = clothing_matcher(doc)

# Print the match ID, start index, end index, and text of each match
for match_id, start, end in matches:
    print(f"Match ID: {match_id}, Start: {start}, End: {end}, Text: {doc[start:end].text}")
