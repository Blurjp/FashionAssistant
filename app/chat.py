import os
import spacy
from spacy.matcher import PhraseMatcher
from spacy.matcher import Matcher
import requests
import openai
import json
import re

nlp = spacy.load("en_core_web_sm")

openai.api_key = os.environ.get("OPENAI_API_KEY")
google_api_key = os.environ.get("GOOGLE_API_KEY")
search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")
google_search_url = "https://www.googleapis.com/customsearch/v1"

# List of fashion brands and clothing items
fashion_brands = [    "Gucci", "Prada", "Versace", "Armani", "Dolce & Gabbana", "Tom Ford", "Chanel", "Dior", "Burberry", "Louis Vuitton","Balenciaga",
                      "Yves Saint Laurent", "Givenchy", "Fendi", "Valentino", "Marc Jacobs", "Michael Kors", "Coach",
                      "Ralph Lauren", "Calvin Klein", "Christian Louboutin", "Alexander McQueen", "Stella McCartney", "Jimmy Choo",
                      "Roberto Cavalli", "Canada Goose", "Lacoste", "Moschino", "Kate Spade", "Diesel", "Hugo Boss", "Miu Miu", "Vivienne Westwood",
                      "Salvatore Ferragamo", "Zara", "H&M", "Uniqlo", "Topshop", "Forever 21", "Gap", "Banana Republic", "ASOS",    "J.Crew", "Levi's",
                      "Lululemon", "Adidas", "Nike", "Puma", "Reebok", "Under Armour", "Converse", "Vans",    "North Face", "Patagonia", "Columbia",
                      "Timberland", "Supreme", "Off-White", "Kenzo", "Heron Preston",    "Stone Island", "A-COLD-WALL*", "A Bathing Ape", "Kith",
                      "Palace", "Stussy", "Goyard", "MCM", "Tory Burch",    "Ted Baker", "Sandro", "Maje", "Massimo Dutti", "Zadig & Voltaire", "AllSaints",
                      "Reformation", "Reiss",    "Hermès", "Bally", "Bottega Veneta", "Balmain", "Celine", "Chloé", "Derek Lam", "Erdem", "Escada",
                      "Etro", "Fausto Puglisi", "Gianvito Rossi", "Isabel Marant", "Jil Sander", "Jonathan Simkhai", "Junya Watanabe",    "Khaite",
                      "Lauren Manoogian", "Loewe", "Maison Margiela", "Max Mara", "Missoni", "Monse", "Nanushka",    "Oscar de la Renta", "Phillip Lim",
                      "Paco Rabanne", "Proenza Schouler", "Roksanda", "Simone Rocha",    "Tibi", "Tod's", "Tory Burch", "Valentino", "Veronica Beard",
                      "Victoria Beckham", "Zimmermann"]


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

# clothing_items = ["coat", "jacket", "shirt", "pants", "jeans", "sweater", "shoes", "boots", "t-shirt", "top", "dress", "skirt", "shorts", "blouse", "hoodie", "socks", "sandals", "sneakers"]

# Create matchers for brands and clothing items
brand_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
brand_patterns = [nlp.make_doc(brand.lower()) for brand in fashion_brands]

# Create a matcher object
clothing_matcher = Matcher(nlp.vocab)
# Create a pattern to capture clothing items, looking for a sequence of adjectives followed by a clothing-related noun
clothing_pattern = [{"POS": "ADJ", "OP": "*"}, {"POS": "NOUN", "LOWER": {"IN": clothing_related_words}}]

# Create a pattern to capture clothing items, looking for a sequence of adjectives and noun compounds followed by a clothing-related noun
clothing_pattern2 = [{"DEP": {"IN": ["amod", "compound"]}}, {"POS": "NOUN", "LEMMA": {"IN": clothing_related_words}}]


brand_matcher.add("BRANDS", brand_patterns)
#clothing_matcher.add("CLOTHING", clothing_patterns)
clothing_matcher.add("CLOTHING", [clothing_pattern, clothing_pattern2])

def extract_items_from_response(response):
    # Find the item list using regular expressions
    item_list = re.findall(r'\n- (.+)', response)
    return item_list

def extract_keywords_from_response(response):

    #response = "For spring in New York, you'll want to dress for changeable weather, as temperatures can range from cool to warm. Here are some ideas:\n\n1. Light layers: A denim or leather jacket worn over a light sweater or tee is the perfect combo for those days when it's cool in the morning but warmer in the afternoon.\n\n2. Midi-length dresses: These versatile dresses are perfect for spring in NYC. Paired with sneakers, flats or heels and a crossbody bag, they're a chic and comfortable option for any day of the week.\n\n3. Crop tops: They're perfect for warmer days and can be dressed up or down. Paired with denim shorts, high-waisted jeans or a midi skirt, they're a fun and fresh look.\n\n4. Chunky sneakers: Comfort is key for all-day walking around the city. You can pair chunky sneakers with dresses, jeans or shorts for a trendy sporty vibe.\n\n5. Monochrome looks: A monochrome look is a great way to stay chic while keeping things simple. Try pairing a cream oversized sweater with white jeans or a gray power suit, for example.\n\nRemember to have fun with your outfits - New York is a fashion-forward city, so don't be afraid to experiment with trends and styles."

    doc = nlp(response)

    # Extract brand names
    brands = brand_matcher(doc)

    # Extract clothing items
    clothes = clothing_matcher(doc)
    # for match_id, start, end in clothes:
    #     print(f"Match ID: {match_id}, Start: {start}, End: {end}, Text: {doc[start:end].text}")
    #
    # print('---------------')
    # for match_id, start, end in brands:
    #     print(f"Match ID: {match_id}, Start: {start}, End: {end}, Text: {doc[start:end].text}")
    #clothes = [doc[start:end].text for match_id, start, end in matches]
    #clothes = clothing_matcher(doc)

    # Extract prices
    prices = [match for match in re.finditer(r'\$[\d,]+(\.\d{2})?', response)]

    distance = 70

    # Find correlated keywords
    correlated_keywords = set()
    for brands_match_id, brand_start, brand_end in brands:
        for clothes_match_id, cloth_start, cloth_end in clothes:
            if abs(brand_end - cloth_start) <= distance or abs(cloth_end - brand_start) <= distance:
                correlated_keyword = doc[brand_start:brand_end].text + " " + doc[cloth_start:cloth_end].text

                # Check for a nearby price
                for price_match in prices:
                    price_start, price_end = price_match.span()
                    if abs(brand_end - price_start) <= distance or abs(cloth_end - price_start) <= distance:
                        correlated_keyword += " " + price_match.group()
                        break

                correlated_keywords.add(correlated_keyword)

    # Handle sentences with only clothes (+ price), only brands (+ price)
    if not correlated_keywords:
        if clothes and not brands:
            for clothes_match_id, cloth_start, cloth_end in clothes:
                correlated_keyword = doc[cloth_start:cloth_end].text

                # Check for a nearby price
                for price_match in prices:
                    price_start, price_end = price_match.span()
                    if abs(cloth_end - price_start) <= distance:
                        correlated_keyword += " " + price_match.group()
                        break

                correlated_keywords.add(correlated_keyword)

        elif brands and not clothes:
            for brands_match_id, brand_start, brand_end in brands:
                correlated_keyword = doc[brand_start:brand_end].text

                # Check for a nearby price
                for price_match in prices:
                    price_start, price_end = price_match.span()
                    if abs(brand_end - price_start) <= distance:
                        correlated_keyword += " " + price_match.group()
                        break

                correlated_keywords.add(correlated_keyword)

    #print("correlated_keywords: ", correlated_keywords)
    return correlated_keywords

# Define a function to filter requests using content moderation.
def filter_request(message):
    # Get the text of the request.
    # text = request.text
    #
    # # Use the OpenAI content moderation endpoint to check if the text is harmful.
    # result = client.moderation(text)
    #
    # # If the text is harmful, return False.
    # if result["score"] > 0.5:
    #     return False
    #
    # # Otherwise, return True.
    # return True

    response = openai.Moderation.create(
        input=message
    )
    output = response["results"][0]["flagged"]
    print(output)
    return output

def send_message_to_chatgpt(message):
    # response = openai.Completion.create(
    #     engine="gpt-3.5-turbo",
    #     prompt=message,
    #     max_tokens=150,
    #     n=1,
    #     stop=None,
    #     temperature=0.7,
    # )
    #filter_request(message)
    #if filter_request(message) == 'false':
    #    return "I'm sorry, I couldn't generate a response. Please try again."

    message = "My message is: " + message + ". If my message is unrelated to fashion shopping and guidance, please say, "'I cannot answer that question because it is unrelated to fashion and shopping.'" " \
               "If my message is related to fashion shopping and guidance, then provide a paragraph as a response and say "'here are the items'", and append a list of fashion items in '-' + adjectives + nouns. "

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful fashion shopping assistant."},
            {"role": "user", "content": message}
        ]
    )
    #print(response)
    if response:
        return response['choices'][0]['message']['content']
    else:
        return "I'm sorry, I couldn't generate a response. Please try again."

def perform_google_search(keywords):
    search_result_number = 6 # Limiting the search results to 20
    results = []
    for keyword in keywords:
        print("query: ", keyword)
        print("google_api_key: ", google_api_key)
        print("cx: ", search_engine_id)
        params = {
            "key": google_api_key,
            "cx": search_engine_id,
            "q": keyword,
            "num": search_result_number,
            "fields": "items(title,link,snippet,pagemap/cse_image/src)" # Adding fields parameter to get title, link, snippet, and image URL
        }

        response = requests.get(google_search_url, params=params)
        search_results = json.loads(response.text)
        print("response.text: ", response.text)
        top_results = search_results.get('items', [])[:search_result_number]  # Extracting the top six results
        for top_result in top_results:
            title = top_result['title']
            link = top_result['link']
            snippet = top_result['snippet']
            image_url = top_result.get('pagemap', {}).get('cse_image', [{}])[0].get('src')  # Extracting the image URL, if available
            print("title:", title)
            print("link:", link)
            print("snippet:", snippet)
            print("image URL:", image_url)

            # Check if the result contains fashion-related keywords
            if contains_fashion_keywords(title) or contains_fashion_keywords(snippet):
                result = {
                    "keyword": keyword,
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "image_url": image_url
                }
                results.append(result)

    return results


def contains_fashion_keywords(text):
    fashion_keywords = ["fashion", "style", "clothing", "apparel", "outfit", "trend"]
    text = text.lower()
    return any(keyword in text for keyword in fashion_keywords)