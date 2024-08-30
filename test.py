from transformers import MarianMTModel, MarianTokenizer

# Функция для перевода текста
def translate(text, model_name):
    # Загружаем токенизатор и модель
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    
    # Токенизация входного текста
    inputs = tokenizer(text, return_tensors="pt", padding=True)
    
    # Генерация перевода
    translated = model.generate(**inputs)
    
    # Декодируем перевод обратно в текст
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    
    return translated_text

# Текст для перевода
text_ru = "Привет, как дела?"
text_en = "Hello, how are you?"

# Перевод с русского на английский
model_name_ru_en = "Helsinki-NLP/opus-mt-ru-en"
translated_text_en = translate(text_ru, model_name_ru_en)
print(f"Перевод с русского на английский: {translated_text_en}")

# Перевод с английского на русский
model_name_en_ru = "Helsinki-NLP/opus-mt-en-ru"
translated_text_ru = translate(text_en, model_name_en_ru)
print(f"Перевод с английского на русский: {translated_text_ru}")