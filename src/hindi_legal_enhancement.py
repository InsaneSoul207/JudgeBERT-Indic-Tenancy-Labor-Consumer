"""
Hindi Statutory Legal Meaning Preservation Corpus Enhancement:
Specially curated pairs to address the Hindi deontic compound modal, statutory exception,
condition, entity swap, and scope gaps across Indian statutes.

Domains covered (unified 3-domain taxonomy):
1. consumer_protection: Consumer Protection Act 2019 & E-Commerce Rules 2020
2. employment_labor: Indian Contract Act 1872, Code on Wages 2019, Gratuity 1972, Maternity 1961, Factories Act 1948, EPF 1952
3. tenancy: Model Tenancy Act 2021 & Transfer of Property Act 1882

Key focus:
- Deontic flips (बाध्य होगा -> चाहे तो कर सकेगा / अनिवार्य -> ऐच्छिक)
- Statutory exceptions (केवल ... छोड़कर / सिवाय -> पूरी तरह हटाया गया)
- Conditional triggers (यदि / बशर्ते कि / जब तक कि -> बिना शर्त)
- Entity swaps (नियोजक <-> कर्मचारी, उपभोक्ता <-> विक्रेता, मकान मालिक <-> किराएदार)
- Scope distortions and timeline shifts
"""

HINDI_DEONTIC_STATUTORY_DATA = [
    {
        "source": "उपभोक्ता संरक्षण अधिनियम 2019, धारा 2(7)",
        "domain": "consumer_protection",
        "clause": "उपभोक्ता से ऐसा कोई व्यक्ति अभिप्रेत है जो किसी ऐसे प्रतिफल के लिए कोई माल खरीदता है जिसका संदाय किया जा चुका है या संदाय किए जाने का वचन दिया गया है, किंतु इसके अंतर्गत वह व्यक्ति नहीं है जो ऐसे माल को पुनर्विक्रय या किसी वाणिज्यिक प्रयोजन के लिए अभिप्राप्त करता है।",
        "simplified_preserved": "उपभोक्ता वह व्यक्ति है जो अपने व्यक्तिगत उपभोग के लिए भुगतान करके सामान या सेवा खरीदता है, और इसमें व्यावसायिक लाभ या पुनर्विक्रय के लिए सामान खरीदने वाले व्यापारी शामिल नहीं हैं।",
        "perturbations": [
            ("उपभोक्ता वह बड़ा थोक व्यापारी है जो सामान को बाजार में दोबारा ऊंचे दामों पर बेचने के व्यावसायिक उद्देश्य से ही खरीदता है।", 1.1, "Not Preserved", "contradiction", "वाणिज्यिक प्रयोजन के अपवर्जन का सीधा विलोम।"),
            ("सामान खरीदने वाले किसी भी व्यक्ति को सामान का मूल्य चुकाने की कोई कानूनी बाध्यता नहीं है।", 1.7, "Not Preserved", "condition", "प्रतिफल के अनिवार्य संदाय की शर्त का लोप।"),
            ("उपभोक्ता वह है जो व्यक्तिगत उपयोग हेतु प्रतिफल देकर माल खरीदता है।", 8.2, "Preserved", "none", "सटीक व संक्षिप्त सरल रूप।"),
            ("उपभोक्ता वह व्यक्ति है जो माल खरीदता है, चाहे वह पुनर्विक्रय के लिए हो या व्यक्तिगत उपयोग हेतु।", 4.4, "Partially Preserved", "exception", "वाणिज्यिक पुनर्विक्रय का कानूनी अपवर्जन हटा दिया गया।")
        ]
    },
    {
        "source": "उपभोक्ता संरक्षण अधिनियम 2019, धारा 84",
        "domain": "consumer_protection",
        "clause": "उत्पाद का कोई निर्माता किसी उत्पाद दायित्व की कार्यवाही में उस नुकसान के लिए दायी होगा जो किसी उत्पाद में विनिर्माण त्रुटि, त्रुटिपूर्ण डिजाइन या पर्याप्त चेतावनी के अभाव के कारण किसी उपभोक्ता को हुआ है।",
        "simplified_preserved": "यदि किसी सामान में बनावटी खराबी, गलत डिजाइन या सुरक्षा चेतावनी न होने से उपभोक्ता को कोई शारीरिक या आर्थिक नुकसान होता है, तो कंपनी हर्जाना देने के लिए कानूनी रूप से उत्तरदायी होगी।",
        "perturbations": [
            ("सामान में कोई भी खराबी होने पर पीड़ित उपभोक्ता को ही कंपनी को भारी हर्जाना चुकाना अनिवार्य होगा।", 1.1, "Not Preserved", "entity", "उत्पाद दायित्व की कानूनी जिम्मेदारी उपभोक्ता पर उल्टी थोप दी गई।"),
            ("कंपनी चाहे तो खराब सामान से हुए नुकसान पर केवल खेद प्रकट कर सकती है, हर्जाना देना पूरी तरह उसकी निजी इच्छा पर निर्भर है।", 2.1, "Not Preserved", "duty_vs_permission", "अनिवार्य विधिक दायित्व को स्वैच्छिक इच्छा में बदल दिया गया।"),
            ("दोषपूर्ण उत्पाद से नुकसान होने पर निर्माता हर्जाने हेतु उत्तरदायी होगा।", 8.8, "Preserved", "none", "सटीक विधिक भाव।"),
            ("दोषपूर्ण उत्पाद के निर्माण से नुकसान होने पर केवल थोक व्यापारी ही नहीं बल्कि उपभोक्ता भी आधा हर्जाना देगा।", 1.8, "Not Preserved", "scope", "दायित्व के क्षेत्र का अनुचित विस्तार।")
        ]
    },
    {
        "source": "उपभोक्ता संरक्षण (ई-कॉमर्स) नियम 2020, नियम 5(3)",
        "domain": "consumer_protection",
        "clause": "कोई भी ई-कॉमर्स संस्था किसी वस्तु या सेवा के संबंध में केवल उस दशा को छोड़कर कोई निरस्तीकरण प्रभार नहीं लगाएगी जब ऐसा प्रभार उस उपभोक्ता द्वारा वहन किया जाना हो जिसने अनुचित रूप से आर्डर रद्द किया है।",
        "simplified_preserved": "ऑनलाइन शॉपिंग कंपनियां ग्राहकों द्वारा ऑर्डर रद्द करने पर मनमाना कैंसलेशन चार्ज नहीं वसूल सकतीं, जब तक कि उपभोक्ता ने स्वयं जानबूझकर बिना कारण ऑर्डर रद्द न किया हो।",
        "perturbations": [
            ("ऑनलाइन कंपनियां हर ऑर्डर पर 100 प्रतिशत अनिवार्य कैंसलेशन चार्ज वसूलने के लिए पूरी तरह स्वतंत्र हैं।", 1.2, "Not Preserved", "contradiction", "कैंसलेशन चार्ज पर सांविधिक रोक का विलोम।"),
            ("कैंसलेशन शुल्क ग्राहक से तभी नहीं लिया जाएगा यदि वेबसाइट बंद हो जाए, अन्यथा ग्राहक को हमेशा पूरा जुर्माना देना होगा।", 2.1, "Not Preserved", "exception", "सांविधिक अपवाद को उलट कर ग्राहक पर बोझ डाला गया।"),
            ("ई-कॉमर्स कंपनियां मनमाना कैंसलेशन चार्ज नहीं ले सकतीं, सिवाय तब जब उपभोक्ता ने स्वयं अनुचित रूप से ऑर्डर रद्द किया हो।", 9.3, "Preserved", "none", "सटीक सरल अर्थ अपवाद सहित।"),
            ("ई-कॉमर्स कंपनियां कोई भी कैंसलेशन चार्ज नहीं ले सकतीं।", 5.6, "Partially Preserved", "omission", "अनुचित रद्दीकरण वाले अपवाद खंड का लोप।")
        ]
    },
    {
        "source": "उपभोक्ता संरक्षण अधिनियम 2019, धारा 35(1)",
        "domain": "consumer_protection",
        "clause": "उपभोक्ता द्वारा या किसी मान्यताप्राप्त उपभोक्ता संगम द्वारा जिला आयोग को परिवाद उस माल या सेवा के संबंध में किया जा सकेगा जिसका प्रतिफल पचास लाख रुपये से अधिक नहीं है।",
        "simplified_preserved": "पचास लाख रुपये तक के मूल्य वाले सामान या सेवा से जुड़े विवाद की शिकायत उपभोक्ता सीधे जिला उपभोक्ता आयोग में दर्ज करा सकता है।",
        "perturbations": [
            ("पचास लाख रुपये तक के विवाद केवल उच्चतम न्यायालय में ही दर्ज कराए जा सकेंगे और जिला आयोग को कोई अधिकार नहीं है।", 1.2, "Not Preserved", "scope", "जिला आयोग के क्षेत्राधिकार का पूर्ण विपर्यास।"),
            ("केवल 500 रुपये तक के मामलों की शिकायत जिला आयोग में की जा सकती है।", 1.9, "Not Preserved", "date_number", "50 लाख रुपये की आर्थिक सीमा घटाकर 500 रुपये कर दी गई।"),
            ("50 लाख रुपये तक के मामलों में जिला आयोग में परिवाद किया जा सकता है।", 9.2, "Preserved", "none", "सटीक विधिक रूप।"),
            ("उपभोक्ता जिला आयोग में परिवाद कर सकता है।", 5.8, "Partially Preserved", "omission", "50 लाख की आर्थिक सीमा छोड़ दी गई।")
        ]
    },
    {
        "source": "उपभोक्ता संरक्षण अधिनियम 2019, धारा 69(1)",
        "domain": "consumer_protection",
        "clause": "जिला आयोग, राज्य आयोग या राष्ट्रीय आयोग किसी परिवाद को तब तक ग्रहण नहीं करेगा जब तक कि वह उस तारीख से, जिसको वाद हेतुक उत्पन्न हुआ है, दो वर्ष के भीतर फाइल न किया गया हो।",
        "simplified_preserved": "उपभोक्ता को विवाद या नुकसान होने की तारीख से दो वर्ष के भीतर ही उपभोक्ता आयोग में शिकायत दर्ज करानी होगी, उसके बाद शिकायत स्वीकार नहीं की जाएगी।",
        "perturbations": [
            ("उपभोक्ता को सामान खरीदने के केवल 7 दिन के भीतर ही शिकायत दर्ज करानी होगी, वरना मामला खारिज हो जाएगा।", 1.8, "Not Preserved", "date_number", "दो वर्ष की वैधानिक परिसीमा को 7 दिन किया गया।"),
            ("उपभोक्ता जीवन में कभी भी, चाहे 20 साल बाद भी, बिना किसी समय सीमा के उपभोक्ता आयोग में शिकायत कर सकता है।", 2.0, "Not Preserved", "condition", "दो वर्ष की अनिवार्य परिसीमा शर्त को समाप्त किया गया।"),
            ("वाद कारण उत्पन्न होने के दो वर्ष के भीतर शिकायत फाइल करना अनिवार्य है।", 9.4, "Preserved", "none", "सटीक परिसीमा नियम संरक्षित।")
        ]
    },
    {
        "source": "मजदूरी संहिता 2019, धारा 17(1)",
        "domain": "employment_labor",
        "clause": "प्रत्येक नियोजक अपने द्वारा नियोजित कर्मचारियों को संदेय समस्त मजदूरी का संदाय मासिक आधार पर आगामी मास के सातवें दिन की समाप्ति से पूर्व करेगा।",
        "simplified_preserved": "मालिक को अपने सभी कर्मचारियों का वेतन हर महीने की 7 तारीख तक अनिवार्य रूप से चुकाना होगा।",
        "perturbations": [
            ("मालिक को वेतन देने की कोई समय सीमा नहीं है और वह चाहे तो 6 महीने बाद मजदूरी दे सकता है।", 1.1, "Not Preserved", "date_number", "मासिक 7 तारीख की समयसीमा 6 महीने में बदल दी गई।"),
            ("मालिक चाहे तो अगले महीने की 7 तारीख तक वेतन दे सकता है, यह उसकी मर्जी पर निर्भर है।", 2.0, "Not Preserved", "duty_vs_permission", "अनिवार्य कर्तव्य को ऐच्छिक बना दिया गया।"),
            ("कर्मचारी को ही हर महीने की 7 तारीख को मालिक को शुल्क अदा करना होगा।", 1.2, "Not Preserved", "entity", "नियोजक और कर्मचारी के कानूनी दायित्व आपस में बदल दिए गए।"),
            ("वेतन का भुगतान अगले महीने की 7 तारीख तक अनिवार्य रूप से करना होगा।", 9.5, "Preserved", "none", "सटीक विधिक रूप।"),
            ("मालिक को कर्मचारियों को मजदूरी देनी होगी।", 5.5, "Partially Preserved", "omission", "मासिक 7 तारीख की वैधानिक समयसीमा हटा दी गई।")
        ]
    },
    {
        "source": "मजदूरी संहिता 2019, धारा 18(1)",
        "domain": "employment_labor",
        "clause": "कर्मचारी की मजदूरी से कोई कटौती इस संहिता के उपबंधों के अधीन प्राधिकृत कटौतियों के सिवाय नहीं की जाएगी।",
        "simplified_preserved": "कानून में दी गई वैध कटौतियों (जैसे पीएफ, टैक्स) के अलावा मालिक कर्मचारी के वेतन में से कोई भी अन्य कटौती नहीं कर सकता।",
        "perturbations": [
            ("मालिक जब चाहे तब कर्मचारी का पूरा वेतन बिना किसी कानूनी कारण के काट सकता है।", 1.1, "Not Preserved", "contradiction", "कटौती निषेध का सीधा उल्लंघन।"),
            ("मालिक बिना किसी कानून या नियम के भी कर्मचारी के वेतन से अपनी मर्जी से कटौती करने का हकदार है।", 1.9, "Not Preserved", "exception", "प्राधिकृत कटौतियों का सांविधिक अपवाद हटाया गया।"),
            ("कानूनी रूप से मान्य कटौतियों के सिवाय मजदूरी से कोई कटौती नहीं की जा सकती।", 9.6, "Preserved", "none", "सटीक विधिक अर्थ।"),
            ("मालिक कर्मचारी के वेतन से कानूनी कटौतियां कर सकता है।", 6.1, "Partially Preserved", "omission", "अवैध कटौतियों पर स्पष्ट रोक का लोप।")
        ]
    },
    {
        "source": "उपदान संदाय अधिनियम 1972, धारा 4(1)",
        "domain": "employment_labor",
        "clause": "उपदान कर्मचारी को उसके नियोजन की समाप्ति पर संदेय होगा यदि उसने कम से कम पांच वर्ष का निरंतर सेवाकाल पूरा कर लिया हो।",
        "simplified_preserved": "किसी संस्थान में लगातार कम से कम 5 वर्ष काम करने के बाद नौकरी छोड़ने या सेवानिवृत्त होने पर कर्मचारी ग्रेच्युटी पाने का कानूनी हकदार है।",
        "perturbations": [
            ("कर्मचारी को ग्रेच्युटी केवल तभी मिलेगी जब वह कम से कम 25 वर्ष तक एक ही कंपनी में काम करे।", 1.4, "Not Preserved", "date_number", "5 वर्ष की पात्रता को 25 वर्ष में बदल दिया गया।"),
            ("कंपनी की मर्जी है कि वह 5 साल बाद ग्रेच्युटी दे या न दे, यह कोई कानूनी बाध्यता नहीं है।", 2.2, "Not Preserved", "duty_vs_permission", "वैधानिक अधिकार को प्रबंधन की इच्छा पर छोड़ दिया गया।"),
            ("यदि कर्मचारी केवल 5 वर्ष की सेवा पूरी किए बिना ही दो महीने में नौकरी छोड़ दे तब भी उसे पूरी ग्रेच्युटी मिलेगी।", 2.0, "Not Preserved", "condition", "5 वर्ष के निरंतर सेवाकाल की अनिवार्य शर्त समाप्त कर दी गई।"),
            ("5 वर्ष की निरंतर सेवा पूरी करने पर कर्मचारी उपदान पाने का हकदार है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।"),
            ("नौकरी समाप्त होने पर कर्मचारी ग्रेच्युटी पाने का हकदार है।", 5.2, "Partially Preserved", "condition", "5 वर्ष की निरंतर सेवा वाली पूर्व शर्त छोड़ दी गई।")
        ]
    },
    {
        "source": "प्रसूति प्रसुविधा अधिनियम 1961, धारा 5(1)",
        "domain": "employment_labor",
        "clause": "प्रत्येक महिला अपने प्रसव के दिन से ठीक पूर्ववर्ती बारह महीनों में कम से कम अस्सी दिन की अवधि के लिए काम करने के पश्चात प्रसूति प्रसुविधा पाने की हकदार होगी।",
        "simplified_preserved": "प्रसव से पहले के 12 महीनों में कम से कम 80 दिन काम करने वाली महिला कर्मचारी सवेतन मातृत्व अवकाश और लाभ पाने की कानूनी हकदार है।",
        "perturbations": [
            ("गर्भवती महिला कर्मचारियों को नौकरी से तुरंत निकाल दिया जाएगा और उन्हें कोई मातृत्व लाभ नहीं मिलेगा।", 1.0, "Not Preserved", "contradiction", "मातृत्व संरक्षण का पूर्णतया उलटफेर।"),
            ("केवल वे महिला कर्मचारी ही मातृत्व लाभ की पात्र होंगी जिन्होंने लगातार 10 वर्ष तक काम किया हो।", 1.8, "Not Preserved", "date_number", "80 दिन / 12 माह की पात्रता को 10 वर्ष में बदला गया।"),
            ("12 महीनों में 80 दिन काम करने वाली महिला प्रसूति लाभ पाने की हकदार है।", 9.4, "Preserved", "none", "सटीक विधिक रूप।"),
            ("महिला कर्मचारी मातृत्व अवकाश और लाभ पा सकती है।", 5.8, "Partially Preserved", "omission", "80 दिन और 12 माह की अहर्ता छोड़ दी गई।")
        ]
    },
    {
        "source": "कारखाना अधिनियम 1948, धारा 51",
        "domain": "employment_labor",
        "clause": "किसी भी वयस्क कर्मकार से किसी कारखाने में किसी सप्ताह में अड़तालीस घंटे से अधिक काम करने की न तो अपेक्षा की जाएगी और न ही उसे ऐसा करने की अनुज्ञा दी जाएगी।",
        "simplified_preserved": "फैक्ट्री में किसी भी बालिग मजदूर से एक हफ्ते में 48 घंटे से ज्यादा काम नहीं लिया जा सकता।",
        "perturbations": [
            ("फैक्ट्री मालिक हर मजदूर से हफ्ते में 84 घंटे अनिवार्य रूप से काम करवाएगा।", 1.1, "Not Preserved", "date_number", "48 घंटे की अधिकतम सीमा का उल्लंघन।"),
            ("प्रत्येक वयस्क मजदूर के लिए सप्ताह में कम से कम 48 घंटे काम करना उसकी अपनी मर्जी पर निर्भर है, अधिक काम भी कराया जा सकता है।", 2.3, "Not Preserved", "duty_vs_permission", "अधिकतम सीमा के निषेध को ऐच्छिक बना दिया गया।"),
            ("एक सप्ताह में वयस्क कर्मकार से अधिकतम 48 घंटे काम लिया जा सकता है।", 9.6, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 73",
        "domain": "employment_labor",
        "clause": "जब कोई संविदा भंग की जाती है तब वह पक्षकार जो ऐसे भंग से नुकसान उठाता है, उस पक्षकार से जिसने संविदा भंग की है, किसी ऐसे नुकसान या क्षति के लिए प्रतिकर पाने का हकदार है जो उस भंग से स्वाभाविक रूप से उत्पन्न हुई हो।",
        "simplified_preserved": "यदि कोई पक्ष समझौता (कॉन्ट्रैक्ट) तोड़ता है, तो पीड़ित पक्ष को उससे हुए वास्तविक और सीधे नुकसान की भरपाई (हर्जाना) पाने का कानूनी अधिकार है।",
        "perturbations": [
            ("समझौता तोड़ने वाला दोषी पक्ष ही पीड़ित पक्ष से उल्टे हर्जाना वसूलने का अधिकारी होगा।", 1.1, "Not Preserved", "entity", "हर्जाना पाने और देने वाले पक्षों की भूमिका उलट दी गई।"),
            ("संविदा भंग होने पर पीड़ित पक्ष काल्पनिक और अनिर्दिष्ट आध्यात्मिक नुकसान के लिए भी अनंत करोड़ रुपये वसूल सकता है।", 2.0, "Not Preserved", "scope", "स्वाभाविक रूप से उत्पन्न वास्तविक क्षति के क्षेत्र को असीमित किया गया।"),
            ("संविदा भंग से हुए स्वाभाविक नुकसान के लिए पीड़ित पक्ष प्रतिकर पाने का हकदार है।", 9.3, "Preserved", "none", "सटीक विधिक भाव।")
        ]
    },
    {
        "source": "आदर्श किराया अधिनियम 2021, धारा 13(1)",
        "domain": "tenancy",
        "clause": "भू-स्वामी या संपत्ति प्रबंधक परिसर के किरायेदार को कम से कम चौबीस घंटे की लिखित पूर्व सूचना दिए बिना, जो इलेक्ट्रॉनिक माध्यम से भी दी जा सकेगी, परिसर में प्रवेश नहीं करेगा।",
        "simplified_preserved": "मकान मालिक कम से कम 24 घंटे पहले लिखित या इलेक्ट्रॉनिक रूप से सूचना दिए बिना किराए के मकान में प्रवेश नहीं कर सकता।",
        "perturbations": [
            ("मकान मालिक दिन-रात कभी भी बिना बताए किराएदार के मकान में सीधे घुसने का असीमित अधिकार रखता है।", 1.1, "Not Preserved", "contradiction", "24 घंटे की पूर्व सूचना व निजता संरक्षण का विलोम।"),
            ("मकान मालिक चाहे तो कभी-कभी सूचना दे सकता है, अन्यथा बिना बताए प्रवेश करना पूरी तरह वैध है।", 2.0, "Not Preserved", "duty_vs_permission", "अनिवार्य सूचना दायित्व को स्वैच्छिक बना दिया गया।"),
            ("किराएदार को ही मकान मालिक के घर में प्रवेश करने के लिए 24 घंटे पहले लिखित अनुमति लेनी होगी।", 1.3, "Not Preserved", "entity", "भू-स्वामी और किराएदार की भूमिका पलट दी गई।"),
            ("किराएदार को 24 घंटे की पूर्व लिखित सूचना दिए बिना मकान मालिक परिसर में प्रवेश नहीं कर सकता।", 9.5, "Preserved", "none", "सटीक विधिक रूप।"),
            ("मकान मालिक परिसर में प्रवेश से पूर्व सूचना देगा।", 5.0, "Partially Preserved", "omission", "24 घंटे की लिखित शर्त छोड़ दी गई।")
        ]
    },
    {
        "source": "आदर्श किराया अधिनियम 2021, धारा 11(1)",
        "domain": "tenancy",
        "clause": "आवासीय परिसर के लिए प्रतिभूति निक्षेप (सिक्योरिटी डिपॉजिट) अधिकतम दो मास के किराये से अधिक नहीं होगा और अनावासीय परिसर के लिए छह मास के किराये से अधिक नहीं होगा।",
        "simplified_preserved": "रहने के मकान के लिए सिक्योरिटी डिपॉजिट अधिकतम 2 महीने का किराया और दुकान या दफ्तर के लिए अधिकतम 6 महीने का किराया ही लिया जा सकता है।",
        "perturbations": [
            ("मकान मालिक रहने के मकान के लिए 24 महीने का किराया सिक्योरिटी डिपॉजिट के रूप में लेने के लिए बाध्य है।", 1.2, "Not Preserved", "date_number", "2 माह की सीमा 24 माह में बदल दी गई।"),
            ("चाहे आवासीय मकान हो या व्यावसायिक दुकान, मकान मालिक को किसी भी सीमा के बिना मनमाना डिपॉजिट लेने की छूट है।", 1.4, "Not Preserved", "scope", "आवासीय व अनावासीय सीमाओं का लोप।"),
            ("रहने के घर हेतु सिक्योरिटी डिपॉजिट अधिकतम दो महीने और दुकान हेतु छह महीने के किराए के बराबर ही हो सकता है।", 9.6, "Preserved", "none", "सटीक विधिक रूप।"),
            ("रहने के घर के लिए सिक्योरिटी डिपॉजिट दो महीने के किराए से अधिक नहीं हो सकता।", 6.4, "Partially Preserved", "omission", "अनावासीय परिसर वाली 6 माह की सीमा छोड़ दी गई।")
        ]
    },
    {
        "source": "संपत्ति अंतरण अधिनियम 1882, धारा 108(m)",
        "domain": "tenancy",
        "clause": "पट्टेदार पट्टे की समाप्ति पर संपत्ति को उसी दशा में छोड़ेगा जिस दशा में वह उस समय थी जब उसे कब्जा दिया गया था, केवल सामान्य घिसावट या अप्रत्याशित दैवीय प्रकोप के नुकसान को छोड़कर।",
        "simplified_preserved": "किराया अवधि समाप्त होने पर किराएदार मकान को वैसी ही अच्छी हालत में लौटाएगा जैसा उसे मिला था, केवल सामान्य पुरानी टूट-फूट या प्राकृतिक आपदा के नुकसान को छोड़कर।",
        "perturbations": [
            ("किराएदार मकान छोड़ते समय दीवारें और छत तोड़कर ही संपत्ति वापस लौटाएगा।", 1.1, "Not Preserved", "contradiction", "संपत्ति सुरक्षित लौटाने के दायित्व का सीधा विलोम।"),
            ("किराएदार को प्राकृतिक आपदा (भूकंप या बाढ़) या सामान्य टूट-फूट से हुए नुकसान की भी पूरी कीमत मकान मालिक को भरनी होगी।", 2.0, "Not Preserved", "exception", "सामान्य घिसावट व दैवीय प्रकोप का वैधानिक अपवाद हटाया गया।"),
            ("पट्टा समाप्त होने पर किराएदार संपत्ति को सामान्य घिसावट छोड़कर अच्छी दशा में वापस सौंपेगा।", 9.1, "Preserved", "none", "सटीक विधिक रूप।"),
            ("किराएदार संपत्ति को अच्छी दशा में वापस सौंपेगा।", 6.0, "Partially Preserved", "exception", "सामान्य घिसावट और प्राकृतिक आपदा के अपवाद छोड़ दिए गए।")
        ]
    },
    # -----------------------------------------------------------------------
    # Additional Labor, Employment & Contract Statutes (Hindi & English)
    # -----------------------------------------------------------------------
    {
        "source": "बोनस संदाय अधिनियम 1965, धारा 10",
        "domain": "employment_labor",
        "language": "hi",
        "clause": "प्रत्येक नियोजक प्रत्येक लेखा वर्ष के संबंध में प्रत्येक कर्मचारी को न्यूनतम बोनस का संदाय करेगा जो कर्मचारी द्वारा उस लेखा वर्ष के दौरान अर्जित वेतन या मजदूरी का 8.33 प्रतिशत होगा या एक सौ रुपये होगा, इनमें से जो भी अधिक हो।",
        "simplified_preserved": "मालिक को हर साल हर पात्र कर्मचारी को कम से कम 8.33 प्रतिशत या 100 रुपये (जो भी ज्यादा हो) न्यूनतम बोनस के रूप में अनिवार्य रूप से देना होगा।",
        "perturbations": [
            ("हर साल मालिक को हर पात्र कर्मचारी को सालाना वेतन का न्यूनतम 8.33% बोनस देना जरूरी है।", 9.4, "Preserved", "none", "सटीक सरल रूप।"),
            ("कंपनी की मर्जी हो तो ही 8.33 प्रतिशत बोनस देगी, कानूनी रूप से कोई न्यूनतम बोनस बाध्यकारी नहीं है।", 2.1, "Not Preserved", "duty_vs_permission", "वैधानिक न्यूनतम बोनस दायित्व को स्वैच्छिक किया गया।"),
            ("कर्मचारी को अपने वेतन का 8.33 प्रतिशत हर साल मालिक को बोनस के तौर पर वापस देना होगा।", 1.2, "Not Preserved", "entity", "नियोजक और कर्मचारी की भुगतान भूमिका उलट दी गई।"),
            ("मालिक कर्मचारी को सालाना बोनस देगा।", 5.5, "Partially Preserved", "omission", "8.33% की न्यूनतम वैधानिक दर हटा दी गई।")
        ]
    },
    {
        "source": "कार्यस्थल पर महिलाओं का लैंगिक उत्पीड़न अधिनियम 2013, धारा 4(1)",
        "domain": "employment_labor",
        "language": "hi",
        "clause": "प्रत्येक नियोजक किसी ऐसे कार्यस्थल पर जहां दस या अधिक कर्मकार नियोजित हैं, लिखित आदेश द्वारा एक आंतरिक शिकायत समिति का गठन करेगा।",
        "simplified_preserved": "जिस कार्यस्थल पर 10 या उससे अधिक कर्मचारी काम करते हैं, वहां के मालिक को लिखित आदेश से आंतरिक शिकायत समिति (ICC) बनाना कानूनी रूप से अनिवार्य है।",
        "perturbations": [
            ("10 या अधिक कर्मचारियों वाले हर दफ्तर में मालिक द्वारा आंतरिक शिकायत समिति गठित करना अनिवार्य है।", 9.5, "Preserved", "none", "सटीक विधिक सारांश।"),
            ("मालिक केवल तभी समिति बनाएगा जब कंपनी में कम से कम 5000 कर्मचारी हों।", 1.7, "Not Preserved", "date_number", "10 कर्मचारियों की सीमा 5000 में बदली गई।"),
            ("10 से ज्यादा कर्मचारी होने पर भी शिकायत समिति बनाना मालिक की निजी इच्छा पर है, कोई कानूनी बाध्यता नहीं है।", 2.0, "Not Preserved", "duty_vs_permission", "अनिवार्य आदेश को ऐच्छिक बना दिया गया।"),
            ("प्रत्येक कार्यस्थल पर आंतरिक शिकायत समिति बनाई जाएगी।", 5.8, "Partially Preserved", "condition", "10 या अधिक कर्मचारियों की शर्त का लोप।")
        ]
    },
    {
        "source": "कर्मचारी राज्य बीमा अधिनियम 1948, धारा 46",
        "domain": "employment_labor",
        "language": "hi",
        "clause": "बीमाकृत व्यक्ति और उनके आश्रित बीमारी, प्रसूति, और रोजगार से हुई चोट या अपंगता की दशा में चिकित्सा उपचार तथा नकद प्रसुविधाएं पाने के हकदार होंगे।",
        "simplified_preserved": "ईएसआई के तहत बीमित कर्मचारी और उसके परिवार के आश्रित सदस्य बीमारी, मातृत्व और कार्यस्थल पर चोट लगने पर मुफ्त इलाज और नकद आर्थिक लाभ पाने के हकदार हैं।",
        "perturbations": [
            ("बीमित कर्मचारी और उसके आश्रित बीमारी व कार्यस्थल की चोट में इलाज तथा नकद लाभ के अधिकारी हैं।", 9.3, "Preserved", "none", "सटीक विधिक रूप।"),
            ("बीमारी या चोट लगने पर बीमित कर्मचारी को कोई इलाज नहीं मिलेगा बल्कि उस पर अलग से जुर्माना लगेगा।", 1.1, "Not Preserved", "contradiction", "वैधानिक सुरक्षा अधिकार का पूर्ण विलोम।"),
            ("केवल कर्मचारी स्वयं इलाज का हकदार है, उसके परिवार के आश्रितों को कोई लाभ नहीं मिलेगा।", 2.4, "Not Preserved", "scope", "आश्रितों के वैधानिक दायरे को समाप्त किया गया।"),
            ("बीमित कर्मचारी चिकित्सा उपचार पाने का हकदार है।", 5.9, "Partially Preserved", "omission", "आश्रितों और नकद प्रसुविधा का लोप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 27",
        "domain": "employment_labor",
        "language": "hi",
        "clause": "हर करार, जिससे कोई व्यक्ति किसी विधिपूर्ण वृत्ति, व्यापार या कारबार के करने से अवरुद्ध किया जाता है, उस विस्तार तक शून्य है।",
        "simplified_preserved": "ऐसा कोई भी समझौता जो किसी व्यक्ति को कोई वैध नौकरी, पेशा या व्यापार करने से रोकता है, उस सीमा तक कानूनी रूप से अमान्य (शून्य) माना जाएगा।",
        "perturbations": [
            ("किसी भी व्यक्ति को कानूनी व्यापार या नौकरी करने से रोकने वाले करार उस हद तक अमान्य होते हैं।", 9.4, "Preserved", "none", "सटीक सरल रूप।"),
            ("कंपनी नौकरी छोड़ने के बाद कर्मचारी को जीवन भर भारत में कोई भी काम करने से रोकने का पूर्णतः वैध करार कर सकती है।", 1.1, "Not Preserved", "contradiction", "व्यापार अवरोध की शून्यता को वैध बंधन में बदला गया।"),
            ("वैध व्यापार से रोकने वाले सभी करार उस विस्तार तक मान्य व लागू करने योग्य हैं।", 1.2, "Not Preserved", "contradiction", "शून्य को मान्य घोषित किया गया।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 56",
        "domain": "employment_labor",
        "language": "hi",
        "clause": "कोई करार, जो अपने आप में असंभव कार्य को करने के लिए हो, प्रारंभ से ही शून्य होता है, और यदि संविदा किए जाने के बाद कार्य करना असंभव या अवैध हो जाए तो संविदा शून्य हो जाती है।",
        "simplified_preserved": "असंभव काम करने का समझौता शुरू से ही अमान्य होता है, और यदि समझौता होने के बाद परिस्थितियों के कारण वह काम असंभव या गैर-कानूनी हो जाए तो समझौता स्वतः समाप्त हो जाता है।",
        "perturbations": [
            ("असंभव या बाद में अवैध हो जाने वाले काम का करार कानूनी रूप से शून्य हो जाता है।", 9.3, "Preserved", "none", "सटीक सरल रूप।"),
            ("कार्य असंभव या गैर-कानूनी हो जाने पर भी पक्षकार को उसे पूरा करना ही होगा वरना उसे जेल भेजा जाएगा।", 1.2, "Not Preserved", "contradiction", "असंभवता के सिद्धांत (फ्रस्ट्रेशन) का विलोम।"),
            ("कोई भी करार जो असंभव काम के लिए हो, शुरू से ही शून्य है।", 5.8, "Partially Preserved", "omission", "संविदा के बाद कार्य असंभव होने वाले द्वितीय खंड का लोप।")
        ]
    },
    {
        "source": "ठेका श्रम (विनियमन और उत्सादन) अधिनियम 1970, धारा 21(4)",
        "domain": "employment_labor",
        "language": "hi",
        "clause": "यदि ठेकेदार निर्धारित अवधि के भीतर मजदूरी का भुगतान करने में विफल रहता है, तो मुख्य नियोजक ठेका श्रमिकों को पूरी मजदूरी का भुगतान करने के लिए उत्तरदायी होगा।",
        "simplified_preserved": "अगर ठेकेदार समय पर मजदूरी नहीं देता है, तो मुख्य नियोक्ता (प्रिंसिपल एम्प्लॉयर) को खुद ठेका मजदूरों का पूरा बकाया वेतन चुकाना होगा।",
        "perturbations": [
            ("ठेकेदार द्वारा वेतन न देने पर मुख्य नियोजक को बकाया मजदूरी का भुगतान करना अनिवार्य होगा।", 9.5, "Preserved", "none", "सटीक विधिक रूप।"),
            ("ठेकेदार द्वारा भुगतान न करने पर ठेका श्रमिकों को ही मुख्य मालिक को दंड देना होगा।", 1.3, "Not Preserved", "entity", "श्रमिक और मुख्य नियोजक के अधिकार उलटे गए।"),
            ("ठेकेदार वेतन न दे तो मुख्य नियोक्ता की कोई कानूनी जिम्मेदारी नहीं है, वह चाहे तो मदद करे या मना कर दे।", 2.0, "Not Preserved", "duty_vs_permission", "मुख्य नियोजक के सांविधिक दायित्व को स्वैच्छिक किया गया।")
        ]
    },
    {
        "source": "Payment of Bonus Act 1965, Section 10",
        "domain": "employment_labor",
        "language": "en",
        "clause": "Subject to the other provisions of this Act, every employer shall be bound to pay to every employee in respect of the accounting year a minimum bonus which shall be 8.33 per cent of the salary or wage earned by the employee during the accounting year or one hundred rupees, whichever is higher.",
        "simplified_preserved": "Every employer must pay eligible employees an annual minimum bonus of 8.33 percent of their yearly wages or 100 rupees, whichever is higher.",
        "perturbations": [
            ("An employer is legally bound to disburse a minimum statutory bonus of 8.33 percent of annual wages to each employee.", 9.4, "Preserved", "none", "Faithful plain statutory summary."),
            ("Employers may optionally award a minimum bonus of 8.33 percent only if company directors feel generous.", 2.2, "Not Preserved", "duty_vs_permission", "Mandatory minimum bonus converted into optional discretion."),
            ("Employees must pay 8.33 percent of their annual salary back to the employer as an employment bonus.", 1.2, "Not Preserved", "entity", "Payor and payee reversed between employer and employee."),
            ("Every employer must pay an annual bonus to employees.", 5.6, "Partially Preserved", "omission", "Mandatory 8.33% rate and 100 rupee floor omitted.")
        ]
    },
    {
        "source": "POSH Act 2013, Section 4(1)",
        "domain": "employment_labor",
        "language": "en",
        "clause": "Every employer of a workplace shall, by an order in writing, constitute a Committee to be known as the Internal Complaints Committee at all administrative units where ten or more employees are employed.",
        "simplified_preserved": "Every employer with 10 or more workers at a workplace must form an Internal Complaints Committee (ICC) through a written order.",
        "perturbations": [
            ("Workplaces employing 10 or more people are legally mandated to set up a written Internal Complaints Committee.", 9.5, "Preserved", "none", "Accurate plain statement."),
            ("Employers need to establish an Internal Complaints Committee only if the company employs more than 2,000 workers.", 1.8, "Not Preserved", "date_number", "Threshold distorted from 10 employees to 2,000 employees."),
            ("Forming an Internal Complaints Committee is completely voluntary even for workplaces with over ten employees.", 2.1, "Not Preserved", "duty_vs_permission", "Mandatory compliance weakened to voluntary choice."),
            ("Every employer shall set up an Internal Complaints Committee.", 5.7, "Partially Preserved", "condition", "10-employee statutory threshold condition omitted.")
        ]
    },
    {
        "source": "Contract Labour Act 1970, Section 21(4)",
        "domain": "employment_labor",
        "language": "en",
        "clause": "In case the contractor fails to make payment of wages within the prescribed period or makes short payment, then the principal employer shall be liable to make payment of wages in full or the unpaid balance due to the contract labour employed by the contractor.",
        "simplified_preserved": "If a contractor fails to pay wages on time or pays less than required, the principal employer becomes legally responsible to pay the remaining wages directly to the contract workers.",
        "perturbations": [
            ("The principal employer must step in and pay any unpaid wage balance if the contractor defaults.", 9.4, "Preserved", "none", "Faithful plain summary."),
            ("The principal employer bears zero legal responsibility if the contractor withholds workers' wages.", 1.3, "Not Preserved", "contradiction", "Principal employer statutory liability completely negated."),
            ("Contract workers are liable to reimburse the principal employer whenever a contractor defaults.", 1.2, "Not Preserved", "entity", "Payment liability shifted onto contract workers."),
            ("The principal employer is liable to pay unpaid wages when the contractor fails.", 8.8, "Preserved", "none", "Valid concise restatement.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 27",
        "domain": "employment_labor",
        "language": "en",
        "clause": "Every agreement by which any one is restrained from exercising a lawful profession, trade or business of any kind, is to that extent void.",
        "simplified_preserved": "Any contract clause that prevents a person from practicing a lawful job, trade, or profession is legally void to that extent.",
        "perturbations": [
            ("Agreements restraining someone from conducting a lawful trade or profession are legally unenforceable.", 9.5, "Preserved", "none", "Accurate plain restatement."),
            ("Agreements banning former workers from ever practicing any lawful profession across the country are strictly binding and enforceable.", 1.1, "Not Preserved", "contradiction", "Section 27 voidness rule inverted into strict enforceability."),
            ("Non-compete agreements stopping a lawful business are valid unless paid compensation.", 2.2, "Not Preserved", "hallucination", "Fabricated validity exception contradicting Section 27.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 56",
        "domain": "employment_labor",
        "language": "en",
        "clause": "An agreement to do an act impossible in itself is void, and a contract to do an act which after the contract is made becomes impossible or unlawful becomes void when the act becomes impossible or unlawful.",
        "simplified_preserved": "An agreement to perform an impossible act is void from the start, and a valid contract becomes automatically void if performance later becomes impossible or illegal.",
        "perturbations": [
            ("Contracts that become impossible or illegal to perform after signing become legally void.", 9.4, "Preserved", "none", "Faithful doctrine of frustration summary."),
            ("Even after performance becomes physically impossible or illegal by statute, a party must still perform the contract or face imprisonment.", 1.2, "Not Preserved", "contradiction", "Doctrine of frustration inverted into mandatory penal enforcement."),
            ("An agreement to do an impossible act is void.", 5.8, "Partially Preserved", "omission", "Omitted supervening impossibility/illegality clause.")
        ]
    },
    {
        "source": "Employees State Insurance Act 1948, Section 46",
        "domain": "employment_labor",
        "language": "en",
        "clause": "The insured persons, their dependants or the persons hereinafter mentioned, as the case may be, shall be entitled to the sickness benefit, maternity benefit, disablement benefit, and medical treatment.",
        "simplified_preserved": "Insured workers and their dependants are legally entitled to sickness pay, maternity benefit, disability compensation, and medical care under ESI.",
        "perturbations": [
            ("Covered workers and dependants are entitled to medical treatment as well as sickness, maternity, and disability benefits.", 9.4, "Preserved", "none", "Accurate plain formulation."),
            ("Only the employer and company directors can claim ESI sickness or medical care, excluding workers and dependants.", 1.3, "Not Preserved", "entity", "Insured beneficiaries replaced by employers."),
            ("Only the worker receives treatment; dependants are permanently barred from medical coverage.", 2.5, "Not Preserved", "scope", "Statutory dependant coverage excluded."),
            ("Insured workers can receive medical treatment under ESI.", 5.9, "Partially Preserved", "omission", "Omitted dependants and cash sickness/maternity/disablement benefits.")
        ]
    }
]
