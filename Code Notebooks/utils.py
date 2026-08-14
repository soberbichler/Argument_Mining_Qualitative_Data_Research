API_MODELS = {
    "Llama3": {
        "provider": "together.ai",
        "entry_point": "meta-llama/Llama-3-70b-chat-hf",
        "max_tokens": 8000
    },
    "Qwen": {
        "provider": "together.ai",
        "entry_point": "Qwen/Qwen2.5-72B-Instruct-Turbo",
        "max_tokens": 8000

    },
    "Nemotron": {
        "provider": "together.ai",
        "entry_point": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
        "max_tokens": 8000
    },
    "DeepSeek": {
        "provider": "deepseek",
        "entry_point": "deepseek-chat",
        "max_tokens": 8000
    },
    "ChatGPT": {
        "provider": "chatgpt",
        "entry_point": "gpt-4o-2024-08-06",
        "max_tokens": 8000
    },
    "Claude": {
        "provider": "anthropic",
        "entry_point": "claude-3-5-sonnet-latest",
        "max_tokens": 8000
    }
}

PARAMETERS = {
    "temperature": 0.0,
    "seed": 42,
    "top_p": 1.0
}

# English
SYSTEM_PROMPT_ENGLISH_SIMPLE ="""You are an expert text analyst and information retrieval specialist and hate summarization as well as enumerations.
Your task is to carefully analyze given texts and extract complete articles that contain specific themes. You never change original texts.

Classify as relevant if the text contains:
- Primary earthquake terminology from the 19th and 20th century
- Official earthquake reports
- geology and seismology
- Impact descriptions
- Solution description
- Technical description
- Aid
- Honorations
- Political discussion and opinions on earthquake
- Stories from victims and refugees
- reportings on refugees and victims
- Live of victims
- historical references
- comparisons

Not relevant are ads and theater or movie announcements.""" #ok ok
SYSTEM_PROMPT_ENGLISH_COMPLEX = """
You are an expert text analyst and information retrieval specialist and hate summarization as well as enumerations.
Your task is to carefully analyze given texts and extract complete articles that contain specific themes only on the Messina earthquake 1908 and the direct consequences of the earthquake (until march 1909) . You never change original texts.

Classify as relevant if the text contains:
- Primary earthquake terminology from the 19th and 20th century
- Official earthquake reports
- gelogy and seismology
- Impact descriptions
- Solution description
- Technical description
- Aid
- Political discussion and opinions on earthquake
- Stories from victims and refugees
- reportings on refugees and victims
- Live of victims
- historical references
- comparisons

Your output should consist of nothing else but the the xml structure >article></article><verification></verification><human_verification_needed></human_verification_needed> or "No relevant article found."

Maintain a neutral, objective stance throughout the analysis. Focus on accuracy and completeness in your extractions""" #ok ok

USER_PROMPT_ENGLISH_COMPLEX  = """
Please follow these specifications:
1. Definition of an article: An article is a semantic unit in the text, clearly distinguished from preceding and following content (e.g., through its own headline).
2. Relevance criteria: An article is relevant if it has the Messina earthquake of December 1908 or its consequences are a topic. Relevant articles, next to the reports on the earthquake, can include:
• Effects on the population (e.g., health crises, forced relocations, relief efforts and donations)
• Aftershocks and consequences
• Political and economic developments related to the earthquake
3. Response format:
• If one or more relevant articles are found, structure your response using XML tags as shown in the following example, using the tags article, verification, confidence and human_verification_needed (True or False): <article>complete extracted article content</article><verification>Is unit coherent? Is topic present? Is article complete? All articles found?</verification><human_verification_needed>False</human_verification_needed><confidence>0.8</confidence><confidence_explanation>explain your confidence estimation</confidence_explanation>
• Return all relevant articles in their original form, without additions, omissions, corrections, or comments.
• If no relevant articles about the Messina earthquake are found (e.g., if it concerns another earthquake),return "No relevant article found." with human verification and confidence estimation.
4. Notes on segmentation:
• Ensure that articles spread across multiple paragraphs are treated as a single unit.
• Never truncate for brevity
5. Human verification needed:
• Can have the values "True" or "False"
• False: If you believe you have correctly segmented the article and assessed its relevance.
• True: If you are unsure whether you have captured the complete content of the article as contained in the newspaper document or whether it is relevant or you are unsure about the right answer.
6. Confidence about correcntess of the answer:
• Can be a number between 0 and 1
• Low confidence means that your confidence in extracting the correct and full article is low
• High confidence means that your confidence in extracting the correct and full article is high

Here is the newspaper document:

""" #ok ok
USER_PROMPT_ENGLISH_COMPLEX2 = """
Please follow these specifications:
1.	Definition of an article: An article is a semantic unit in the text, clearly distinguished from preceding and following content (for example, may or may not have a title).
2.	Relevance criteria: An article is relevant if its main subject is the Messina earthquake of December 1908 or its consequences. Other earthquakes are not relevant. The relevant consequences are mentioned in the system prompt. Make sure to check the publication date. --> Keep international news sections together: Example Jena, January 8. The local geologist, Dr. Gravelitz, has established that the seabed of the Strait of Messina has become silted up in places following the earthquake. At some points, soundings show only fifteen feet of depth. Rome, January 9. General Mazza has telegraphed to the Prime Minister that it will be possible to recover all funds and archives of public services from the ruins of Reggio di Calabria. Railway communication between Reggio and Naples will be restored within three days.
3.	Response format:
• If one or more relevant articles are found, structure your response using XML tags as shown in the following example, using the tags article, verification, confidence and human_verification_needed (True or False): <article>complete content of extracted article 1</article><article>complete content of extracted article 2</article><verification>Is the unit coherent? Is the subject present? Is the article complete? Have all articles been found?</verification><human_verification_needed>False</human_verification_needed><confidence>0.8</confidence><confidence_explanation>explain your confidence estimation</confidence_explanation>
• Return all relevant articles in their original form, without additions, omissions, corrections or comments. Never cut content between the beginning and end of an article.
• If no relevant articles about the Messina earthquake are found (for example, if it concerns another earthquake),  return "No relevant article found." with human verification and confidence estimation.
4.	Notes on segmentation:
• Ensure that articles form a unit. Be sure to mark each separate unit (marked by a new title or new semantic unit) as a new article <article></article>)
5.	Human verification needed:
• Can have values "True" or "False"
• False: If you think you have correctly segmented the article and evaluated its relevance. • True: If you are unsure whether you have captured the complete content of the article as contained in the newspaper document or if it is relevant.
6.	Confidence about correctness of the answer:
• Can be a number between 0 and 1
• Low confidence means that your confidence in extracting the correct and full article is low
• High confidence means that your confidence in extracting the correct and full article is high
7.	Check verification results and adapt response if necessary
Here is the newspaper document:


""" #ok ok
USER_PROMPT_ENGLISH_SIMPLE = """
Please identify and extract articles that relate to the severe Messina earthquake in December 1908 or its aftermath in the provided newspaper document. If you don't find any relevant articles relating to this topic, simply return 'No relevant article found.' with human verification and confidence estimation. If you find one or more articles, return their full, unchanged content (beginning to end) structured in xml format, each wrapped in <article> tags, human verification and confidence estimation in tags </verification><human_verification_needed>False</human_verification_needed><confidence>0.8</confidence><confidence_explanation>explain your confidence estimation</confidence_explanation>

""" #ok ok

# French
USER_PROMPT_FRENCH_COMPLEX = """
Veuillez suivre ces spécifications:
1.	Définition d'un article: Un article est une unité sémantique dans le texte, clairement distinguée du contenu précédent et suivant (par exemple, par son propre titre).
2.	Critères de pertinence: Un article est pertinent si le tremblement de terre de Messine de décembre 1908 ou ses conséquences en sont un sujet. Les articles pertinents, en plus des reportages sur le tremblement de terre, peuvent inclure:
• Effets sur la population (par exemple, crises sanitaires, déplacements forcés, efforts de secours et dons)
• Répliques et conséquences
• Développements politiques et économiques liés au tremblement de terre
3.	Format de réponse:
• Si vous trouvez un ou plusieurs articles pertinents, structurez votre réponse en utilisant des balises XML comme indiqué dans l'exemple suivant, en utilisant les balises article, verification, confidence et human_verification_needed (True ou False): <article>contenu complet de l'article extrait</article><verification>L'unité est-elle cohérente? Le sujet est-il présent? L'article est-il complet? Tous les articles ont-ils été trouvés?</verification><human_verification_needed>False</human_verification_needed><confidence>0.8</confidence><confidence_explanation>explain your confidence estimation</confidence_explanation>
• Renvoyez tous les articles pertinents dans leur forme originale, sans ajouts, omissions, corrections ou commentaires.
• Si vous ne trouvez aucun article pertinent sur le tremblement de terre de Messine (par exemple, s'il concerne un autre tremblement de terre), retournez "Aucun article pertinent trouvé."  avec une vérification humaine et une estimation de la fiabilité.
4.	Notes sur la segmentation:
• Assurez-vous que les articles répartis sur plusieurs paragraphes sont traités comme une seule unité.
• Ne jamais tronquer par souci de concision
5.	Vérification humaine nécessaire:
• Peut avoir les valeurs "True" ou "False"
• False: Si vous pensez avoir correctement segmenté l'article et évalué sa pertinence.
• True: Si vous n'êtes pas sûr d'avoir capturé le contenu complet de l'article tel qu'il figure dans le document de journal ou s'il est pertinent ou si vous n'êtes pas sûr de la bonne réponse.
6.	Confiance dans l'exactitude de la réponse:
• Peut être un nombre entre 0 et 1
• Une faible confiance signifie que votre confiance dans l'extraction de l'article correct et complet est faible
• Une confiance élevée signifie que votre confiance dans l'extraction de l'article correct et complet est élevée
Voici le document de journal:

""" #ok ok
USER_PROMPT_FRENCH_SIMPLE = """
Merci d’identifier et d’extraire les articles qui concernent le violent tremblement de terre de Messine en décembre 1908 ou ses conséquences, à partir du document de presse fourni.
Si tu ne trouves aucun article pertinent sur ce sujet, retourne simplement « Aucun article pertinent trouvé. » avec une vérification humaine et une estimation de la fiabilité.
Si tu trouves un ou plusieurs articles, retourne leur contenu complet et inchangé (du début à la fin) au format XML, chaque article étant encadré par des balises <article>, et ajoute la vérification humaine et l’estimation de la fiabilité dans les balises </verification><human_verification_needed>False</human_verification_needed><confidence>0.8</confidence><confidence_explanation>Explique ton estimation de la fiabilité</confidence_explanation>.
""" #ok ok

# German
USER_PROMPT_GERMAN_COMPLEX = """

Bitte folge diesen Spezifikationen:
1.	Definition eines Artikels: Ein Artikel ist eine semantische Einheit im Text, die sich deutlich vom vorherigen und nachfolgenden Inhalt unterscheidet (z.B. durch eine eigene Überschrift).
2.	Relevanzkriterien: Ein Artikel ist relevant, wenn das Erdbeben von Messina vom Dezember 1908 oder seine Folgen ein Thema sind. Relevante Artikel können neben den Berichten über das Erdbeben Folgendes umfassen:
• Auswirkungen auf die Bevölkerung (z.B. Gesundheitskrisen, Zwangsumsiedlungen, Hilfsmaßnahmen und Spenden)
• Nachbeben und Folgen
• Politische und wirtschaftliche Entwicklungen im Zusammenhang mit dem Erdbeben
3.	Antwortformat:
• Wenn du ein oder mehrere relevante Artikel findest, strukturiere deine Antwort mit XML-Tags wie im folgenden Beispiel gezeigt, unter Verwendung der Tags article, verification, confidence und human_verification_needed (True oder False): <article>vollständiger extrahierter Artikelinhalt</article><verification>Ist die Einheit kohärent? Ist das Thema vorhanden? Ist der Artikel vollständig? Wurden alle Artikel gefunden?</verification><human_verification_needed>False</human_verification_needed><confidence>0.8</confidence><confidence_explanation>explain your confidence estimation</confidence_explanation>
• Gib alle relevanten Artikel in ihrer ursprünglichen Form zurück, ohne Ergänzungen, Auslassungen, Korrekturen oder Kommentare. • Wenn keine relevanten Artikel über das Erdbeben von Messina gefunden werden (z.B. wenn es um ein anderes Erdbeben geht), gib "Kein relevanter Artikel gefunden." zurück mit human verification und confidence estimation.
4.	Hinweise zur Segmentierung:
• Stelle sicher, dass über mehrere Absätze verteilte Artikel als eine Einheit behandelt werden.
• Niemals aus Gründen der Kürze abschneiden
5.	Menschliche Überprüfung erforderlich:
• Kann die Werte "True" oder "False" haben
• False: Wenn du glaubst, dass du den Artikel korrekt segmentiert und seine Relevanz beurteilt hast.
• True: Wenn du unsicher bist, ob du den vollständigen Inhalt des Artikels erfasst hast, wie er im Zeitungsdokument enthalten ist, oder ob er relevant ist, oder wenn du dir über die richtige Antwort unsicher bist.
6.	Vertrauen in die Richtigkeit der Antwort: • Kann eine Zahl zwischen 0 und 1 sein
• Geringes Vertrauen bedeutet, dass dein Vertrauen in die Extraktion des korrekten und vollständigen Artikels gering ist
• Hohes Vertrauen bedeutet, dass dein Vertrauen in die Extraktion des korrekten und vollständigen Artikels hoch ist
Hier ist das Zeitungsdokument:

""" #ok ok
USER_PROMPT_GERMAN_SIMPLE = """
Bitte identifiziere und extrahiere Artikel, die sich auf das schwere Erdbeben von Messina im Dezember 1908 oder dessen Folgen beziehen, aus dem bereitgestellten Zeitungsdokument.
Wenn du keine relevanten Artikel zu diesem Thema findest, gib einfach „Kein relevanter Artikel gefunden.“ zurück – zusammen mit einer menschlichen Verifizierung und einer Schätzung der Zuverlässigkeit.
Wenn du einen oder mehrere Artikel findest, gib deren vollständigen, unveränderten Inhalt (von Anfang bis Ende) im XML-Format zurück, wobei jeder Artikel in <article>-Tags eingebettet ist, und füge die menschliche Verifizierung und die Zuverlässigkeitsschätzung in den Tags </verification><human_verification_needed>False</human_verification_needed><confidence>0.8</confidence><confidence_explanation>Erkläre deine Zuverlässigkeitsschätzung</confidence_explanation> hinzu.""" #ok ok


USER_PROMPT_LANG_STYLE = {
    "french": {
        "simple": USER_PROMPT_FRENCH_SIMPLE,
        "complex": USER_PROMPT_FRENCH_COMPLEX
    },
    "german": {
        "simple": USER_PROMPT_GERMAN_SIMPLE,
        "complex": USER_PROMPT_GERMAN_COMPLEX
    },
    "english": {
        "simple": USER_PROMPT_ENGLISH_SIMPLE,
        "complex": USER_PROMPT_ENGLISH_COMPLEX,
        "complex2": USER_PROMPT_ENGLISH_COMPLEX2
    }
}

SYSTEM_PROMPT_LANG_STYLE = {
    "english": {
        "simple": SYSTEM_PROMPT_ENGLISH_SIMPLE,
        "complex": SYSTEM_PROMPT_ENGLISH_COMPLEX
    }
}


