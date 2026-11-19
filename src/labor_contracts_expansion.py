"""
Authentic Statutory Provisions and Perturbations for Employment, Labor & Contract Law.
Covers:
1. Indian Contract Act 1872 (Free consent, coercion, undue influence, fraud, misrepresentation,
   lawful consideration, wager, certainty, novation, pledge, agency)
2. Payment of Gratuity Act 1972 (Section 7 - payment timeline)
3. Maternity Benefit Act 1961 (Section 12 - unlawful dismissal during maternity leave)
4. Employees' Provident Funds Act 1952 (Section 14 - penalties for default)
5. Employees' Compensation Act 1923 (Section 4 - minimum compensation floor)
6. Industrial Relations Code 2020 / ID Act 1947 (Strike notice, lay-off compensation, unfair labor practices)
7. Factories Act 1948 (Overcrowding, machinery fencing, child labor prohibition, annual leave with wages)
"""

EXTRA_LABOR_STATUTORY_EN = [
    {
        "source": "Payment of Gratuity Act 1972, Section 7(3)",
        "clause": "The employer shall arrange to pay the amount of gratuity within thirty days from the date it becomes payable to the person to whom the gratuity is payable.",
        "simplified_preserved": "An employer must pay the full gratuity amount to the entitled employee within 30 days from when it becomes due.",
        "perturbations": [
            ("An employer may defer gratuity payments for up to twenty years without interest.", 1.2, "Not Preserved", "date_number", "30-day statutory payment window extended to 20 years."),
            ("Employees are required to pay gratuity to the employer within 30 days of resigning.", 1.1, "Not Preserved", "entity", "Gratuity payment obligation inverted from employer to employee."),
            ("The employer must disburse the gratuity within thirty days of it becoming due.", 9.5, "Preserved", "none", "Accurate statutory plain restatement.")
        ]
    },
    {
        "source": "Maternity Benefit Act 1961, Section 12(1)",
        "clause": "When a woman absents herself from work in accordance with the provisions of this Act, it shall be unlawful for her employer to discharge or dismiss her during or on account of such absence.",
        "simplified_preserved": "It is completely illegal for an employer to fire or dismiss a female employee because she took statutory maternity leave.",
        "perturbations": [
            ("Employers are legally mandated to fire any female worker the moment she applies for maternity leave.", 1.1, "Not Preserved", "contradiction", "Protection against dismissal inverted into mandatory termination."),
            ("An employer cannot lawfully terminate a woman employee while she is on maternity leave.", 9.5, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Employees Provident Funds Act 1952, Section 14(1)",
        "clause": "Whoever, for the purpose of avoiding any payment to be made by himself under this Act or of enabling any other person to avoid such payment, knowingly makes or causes to be made any false statement or false representation, shall be punishable with imprisonment for a term which may extend to one year, or with fine of four thousand rupees, or with both.",
        "simplified_preserved": "Anyone who makes false statements to evade statutory Provident Fund payments faces up to one year in prison, a 4,000 rupee fine, or both.",
        "perturbations": [
            ("Falsifying PF records to evade employee retirement benefits is officially rewarded with a tax deduction.", 1.1, "Not Preserved", "contradiction", "Criminal penal sanction turned into official financial reward."),
            ("Evading PF contributions through false statements is punishable by up to one year in prison or a fine.", 9.4, "Preserved", "none", "Faithful plain formulation.")
        ]
    },
    {
        "source": "Employees Compensation Act 1923, Section 4(1)",
        "clause": "Where death results from the injury, the amount of compensation shall be an amount equal to fifty per cent of the monthly wages of the deceased employee multiplied by the relevant factor, or an amount as may be notified by the Central Government, whichever is more.",
        "simplified_preserved": "In case of a fatal workplace accident, compensation is 50 percent of monthly wages multiplied by the age factor, or the government minimum floor, whichever is higher.",
        "perturbations": [
            ("The family of a deceased worker must pay fifty percent of the factory's monthly electricity bill.", 1.1, "Not Preserved", "entity", "Compensation recipient and payor completely inverted."),
            ("Workplace death compensation equals 50 percent of monthly wages multiplied by the statutory factor.", 9.3, "Preserved", "none", "Accurate plain summary.")
        ]
    },
    {
        "source": "Industrial Relations Code 2020, Section 62(1)",
        "clause": "No person employed in an industrial establishment shall go on strike in breach of contract without giving to the employer notice of strike, as hereinafter provided, within sixty days before striking, or within fourteen days of giving such notice.",
        "simplified_preserved": "Industrial workers cannot legally go on strike without giving their employer at least 14 days advance written notice within 60 days before the strike.",
        "perturbations": [
            ("Workers can stage unannounced surprise strikes at any second without ever notifying the employer.", 1.2, "Not Preserved", "condition", "Mandatory 14-day statutory strike notice requirement erased."),
            ("Strikes require advance notice of at least fourteen days to the employer.", 9.4, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Industrial Relations Code 2020, Section 67",
        "clause": "Whenever a workman whose name is borne on the muster rolls of an industrial establishment is laid off, he shall be paid by the employer for all days during which he is so laid off, compensation which shall be equal to fifty per cent of the total of the basic wages and dearness allowance.",
        "simplified_preserved": "A laid-off industrial worker is legally entitled to compensation equal to 50 percent of their basic wage and dearness allowance for the lay-off period.",
        "perturbations": [
            ("Laid-off workers must forfeit their entire life savings to the factory management.", 1.1, "Not Preserved", "contradiction", "50% lay-off compensation converted to asset confiscation."),
            ("Laid-off workers are entitled to 50 percent of basic wages and dearness allowance as compensation.", 9.5, "Preserved", "none", "Faithful plain restatement.")
        ]
    },
    {
        "source": "Industrial Relations Code 2020, Section 86",
        "clause": "No employer or workman or a trade union, whether registered under this Code or not, shall commit any unfair labour practice specified in the Second Schedule.",
        "simplified_preserved": "Employers, workers, and trade unions are strictly prohibited from engaging in any unfair labor practices recognized under the law.",
        "perturbations": [
            ("Employers are legally mandated to engage in unfair labor practices and union-busting as daily routine.", 1.1, "Not Preserved", "contradiction", "Statutory ban on unfair labor practices inverted into positive duty."),
            ("Engaging in unfair labor practices is prohibited for employers and unions alike.", 9.5, "Preserved", "none", "Direct plain summary.")
        ]
    },
    {
        "source": "Factories Act 1948, Section 16(1)",
        "clause": "No room in any factory shall be overcrowded to an extent injurious to the health of the workers employed therein, and there shall be provided for every worker employed in a workroom at least 14.2 cubic metres of space.",
        "simplified_preserved": "Factory workrooms must never be dangerously overcrowded and must provide at least 14.2 cubic meters of breathing space per worker.",
        "perturbations": [
            ("Factory owners must pack at least 500 workers into every one-meter closet to maximize factory output.", 1.1, "Not Preserved", "scope", "Health safety threshold distorted into extreme hazardous congestion."),
            ("Factory rooms must not be overcrowded and must provide at least 14.2 cubic meters of space per worker.", 9.4, "Preserved", "none", "Accurate plain summary.")
        ]
    },
    {
        "source": "Factories Act 1948, Section 21(1)",
        "clause": "In every factory, every dangerous part of any machinery shall be securely fenced by safeguards of substantial construction which shall be constantly maintained and kept in position while the parts of machinery they are fencing are in motion.",
        "simplified_preserved": "All dangerous moving machinery parts in a factory must be securely and permanently fenced with sturdy safety guards while in operation.",
        "perturbations": [
            ("Factory managers are encouraged to remove all machine guards so workers can touch exposed spinning blades.", 1.1, "Not Preserved", "contradiction", "Mandatory machine fencing converted into reckless deliberate hazard."),
            ("Dangerous machinery in factories must be securely fenced with safety guards while operating.", 9.5, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Factories Act 1948, Section 67",
        "clause": "No child who has not completed his fourteenth year shall be required or allowed to work in any factory.",
        "simplified_preserved": "Children under the age of 14 are strictly prohibited from being employed or working in any factory.",
        "perturbations": [
            ("Children aged five and above are legally compelled to work 16 hours daily in heavy factories.", 1.1, "Not Preserved", "contradiction", "Child labor prohibition inverted into compulsory child exploitation."),
            ("Children under 14 cannot be required or permitted to work in any factory.", 9.6, "Preserved", "none", "Accurate statutory plain restatement.")
        ]
    },
    {
        "source": "Factories Act 1948, Section 79(1)",
        "clause": "Every worker who has worked for a period of 240 days or more in a factory during a calendar year shall be allowed during the subsequent calendar year leave with wages at the rate of one day for every twenty days of work performed.",
        "simplified_preserved": "Factory workers completing 240 days of work in a year earn paid annual leave at the rate of one day for every 20 working days.",
        "perturbations": [
            ("Workers who work 240 days must pay a fine of one month's wage and are barred from ever taking leave.", 1.2, "Not Preserved", "contradiction", "Paid statutory leave converted to punitive fine."),
            ("Workers completing 240 days earn paid annual leave of one day per twenty days worked.", 9.4, "Preserved", "none", "Faithful plain formulation.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 14",
        "clause": "Consent is said to be free when it is not caused by coercion, undue influence, fraud, misrepresentation, or mistake, subject to the provisions of sections 20, 21 and 22.",
        "simplified_preserved": "Consent in a contract is considered legally free only when it is not obtained through threats, manipulation, deceit, false claims, or mutual mistake.",
        "perturbations": [
            ("Consent is legally defined as valid only when obtained through armed extortion and physical terror.", 1.1, "Not Preserved", "contradiction", "Definition of free consent inverted into coercive duress."),
            ("Contractual consent is free when not caused by coercion, undue influence, fraud, or mistake.", 9.5, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 15",
        "clause": "Coercion is the committing, or threatening to commit, any act forbidden by the Indian Penal Code, or the unlawful detaining, or threatening to detain, any property, to the prejudice of any person whatever, with the intention of causing any person to enter into an agreement.",
        "simplified_preserved": "Coercion means committing or threatening illegal criminal acts or unlawfully seizing someone's property to force them into signing an agreement.",
        "perturbations": [
            ("Coercion is legally approved as the primary recommended method for government contract signing.", 1.1, "Not Preserved", "contradiction", "Unlawful coercion legitimized as recommended practice."),
            ("Coercion is using unlawful threats or property detention to force someone to enter a contract.", 9.4, "Preserved", "none", "Accurate plain summary.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 16(1)",
        "clause": "A contract is said to be induced by undue influence where the relations subsisting between the parties are such that one of the parties is in a position to dominate the will of the other and uses that position to obtain an unfair advantage over the other.",
        "simplified_preserved": "Undue influence occurs when one party holds psychological or authoritative power over another and abuses that dominance to secure an unfair contractual benefit.",
        "perturbations": [
            ("Undue influence is when two equal strangers trade goods in a competitive public auction.", 1.5, "Not Preserved", "scope", "Distorted into standard arm's-length open transaction."),
            ("Undue influence happens when a dominant party exploits their position to gain an unfair advantage.", 9.5, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 17",
        "clause": "Fraud means and includes the suggestion, as a fact, of that which is not true, by one who does not believe it to be true, or the active concealment of a fact, with intent to deceive another party or to induce him to enter into the contract.",
        "simplified_preserved": "Fraud involves intentionally asserting false information or deliberately concealing material facts to trick another person into entering an agreement.",
        "perturbations": [
            ("Fraud is when a seller provides completely accurate facts and honors all contractual promises in good faith.", 1.1, "Not Preserved", "contradiction", "Fraud definition inverted into honest performance."),
            ("Fraud means intentional deception or active concealment of facts to induce a contract.", 9.5, "Preserved", "none", "Faithful plain formulation.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 18",
        "clause": "Misrepresentation means and includes the positive assertion, in a manner not warranted by the information of the person making it, of that which is not true, though he believes it to be true, or any breach of duty which gains an advantage by misleading another.",
        "simplified_preserved": "Misrepresentation is making an inaccurate statement of fact without justified grounds, even if genuinely believed, which misleads another party into an agreement.",
        "perturbations": [
            ("Misrepresentation is legally defined as speaking only absolute verified scientific truths under oath.", 1.1, "Not Preserved", "contradiction", "Misrepresentation flipped into verified truth."),
            ("Misrepresentation is making unwarranted false statements that mislead a party into contracting.", 9.4, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 23",
        "clause": "The consideration or object of an agreement is lawful, unless it is forbidden by law, or is of such a nature that, if permitted, it would defeat the provisions of any law, or is fraudulent, or involves injury to the person or property of another, or the Court regards it as immoral or opposed to public policy.",
        "simplified_preserved": "A contract's purpose and consideration are lawful unless illegal, fraudulent, harmful to individuals or property, immoral, or harmful to public policy.",
        "perturbations": [
            ("Agreements to murder innocent citizens and burn down public schools are declared fully lawful objects.", 1.1, "Not Preserved", "contradiction", "Unlawful consideration provisions completely inverted."),
            ("Contract consideration is lawful unless illegal, fraudulent, injurious, or contrary to public policy.", 9.5, "Preserved", "none", "Accurate plain summary.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 25",
        "clause": "An agreement made without consideration is void, unless it is expressed in writing and registered under the law for the time being in force for the registration of documents, and is made on account of natural love and affection between parties standing in a near relation to each other.",
        "simplified_preserved": "An agreement without consideration is legally void, except when documented in writing, registered, and made out of natural love between close family relatives.",
        "perturbations": [
            ("All commercial agreements without payment or consideration are automatically valid and enforceable against strangers.", 1.2, "Not Preserved", "contradiction", "Rule that agreements without consideration are void negated."),
            ("Agreements without consideration are void unless in writing, registered, and between close relatives.", 9.4, "Preserved", "none", "Faithful plain restatement.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 29",
        "clause": "Agreements, the meaning of which is not certain, or capable of being made certain, are void.",
        "simplified_preserved": "Any agreement whose essential terms are vague, ambiguous, or impossible to determine with certainty is legally void and unenforceable.",
        "perturbations": [
            ("Agreements that are completely incomprehensible and gibberish must be enforced strictly by all courts.", 1.1, "Not Preserved", "contradiction", "Uncertain agreements rule inverted into mandatory enforcement of nonsense."),
            ("Agreements whose terms cannot be made certain are legally void.", 9.6, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 30",
        "clause": "Agreements by way of wager are void; and no suit shall be brought for recovering anything alleged to be won on any wager, or entrusted to any person to abide the result of any game or other uncertain event on which any wager is made.",
        "simplified_preserved": "Gambling and wagering agreements are legally void, and courts will not entertain any lawsuit to collect gambling debts or bet winnings.",
        "perturbations": [
            ("The High Court operates as an enforcement debt collector for underground cricket betting syndicates.", 1.1, "Not Preserved", "contradiction", "Wager unenforceability flipped into judicial debt collection."),
            ("Wagering agreements are legally void and gambling winnings cannot be recovered in court.", 9.5, "Preserved", "none", "Accurate plain summary.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 39",
        "clause": "When a party to a contract has refused to perform, or disabled himself from performing, his promise in its entirety, the promisee may put an end to the contract, unless he has signified, by words or conduct, his acquiescence in its continuance.",
        "simplified_preserved": "If a party outright refuses to fulfill their contractual promise, the other party has the legal right to cancel and terminate the contract.",
        "perturbations": [
            ("If a builder refuses to build the house, the buyer is legally forced to continue paying them forever without cancellation.", 1.2, "Not Preserved", "contradiction", "Right of contract repudiation inverted."),
            ("When a party refuses to perform their promise, the other party may terminate the contract.", 9.5, "Preserved", "none", "Faithful plain summary.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 62",
        "clause": "If the parties to a contract agree to substitute a new contract for it, or to rescind or alter it, the original contract need not be performed.",
        "simplified_preserved": "When parties mutually agree to replace, cancel, or modify an existing contract, they are discharged from performing the original agreement.",
        "perturbations": [
            ("Parties who sign a new replacement contract are still criminally liable to execute the deleted old agreement simultaneously.", 1.2, "Not Preserved", "contradiction", "Novation discharge inverted into simultaneous liability."),
            ("Parties who replace or alter a contract through mutual agreement need not perform the original contract.", 9.5, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 65",
        "clause": "When an agreement is discovered to be void, or when a contract becomes void, any person who has received any advantage under such agreement or contract is bound to restore it, or to make compensation for it to the person from whom he received it.",
        "simplified_preserved": "If a contract is discovered to be legally void, anyone who received money, goods, or benefits under it must return them or pay fair compensation.",
        "perturbations": [
            ("Anyone receiving an advance payment on an illegal void contract is entitled to steal it and keep all profits.", 1.1, "Not Preserved", "contradiction", "Restitution requirement inverted into theft entitlement."),
            ("When a contract is void, anyone who received an advantage must return it or compensate the other party.", 9.5, "Preserved", "none", "Faithful plain formulation.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 172",
        "clause": "The bailment of goods as security for payment of a debt or performance of a promise is called pledge. The bailor is in this case called the pawnor. The bailee is called pawnee.",
        "simplified_preserved": "A pledge is handing over physical goods or valuables as collateral security to guarantee repayment of a loan or performance of a promise.",
        "perturbations": [
            ("A pledge means the lender permanently owns the borrower's house with no obligation to return it upon debt repayment.", 1.2, "Not Preserved", "contradiction", "Pledge collateral converted into permanent forfeiture."),
            ("A pledge is the delivery of goods as collateral security for a debt or promise.", 9.5, "Preserved", "none", "Accurate plain summary.")
        ]
    },
    {
        "source": "Indian Contract Act 1872, Section 182",
        "clause": "An agent is a person employed to do any act for another, or to represent another in dealings with third persons. The person for whom such act is done, or who is so represented, is called the principal.",
        "simplified_preserved": "An agent is someone authorized to act on behalf of or legally represent another person (called the principal) in business dealings with third parties.",
        "perturbations": [
            ("An agent is legally prohibited from ever acting or signing documents on behalf of their principal.", 1.2, "Not Preserved", "contradiction", "Agency authority definition negated."),
            ("An agent is authorized to act or represent another person called the principal.", 9.5, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Code on Social Security 2020, Section 114(1)",
        "clause": "Every aggregator shall contribute to the social security fund for gig workers and platform workers at such rate which shall not exceed two per cent, but not be less than one per cent, of the annual turnover of every such aggregator.",
        "simplified_preserved": "Digital platform aggregators must contribute between 1 and 2 percent of their annual turnover to the government social security fund for gig and platform delivery workers.",
        "perturbations": [
            ("Aggregators are legally prohibited from contributing to gig worker welfare funds.", 1.1, "Not Preserved", "contradiction", "Statutory social security contribution obligation inverted."),
            ("Aggregators must contribute between 1 and 2 percent of annual turnover to the gig worker social security fund.", 9.5, "Preserved", "none", "Faithful plain formulation.")
        ]
    },
    {
        "source": "Occupational Safety Code 2020, Section 32(1)",
        "clause": "In every establishment there shall be provided and maintained sufficient supply of wholesome drinking water and sufficient latrine and urinal accommodation of prescribed types separated for male and female workers.",
        "simplified_preserved": "Every workplace establishment must provide free wholesome drinking water and clean, separate restrooms for male and female employees.",
        "perturbations": [
            ("Employers are strictly forbidden from providing any drinking water or bathrooms to laborers.", 1.1, "Not Preserved", "contradiction", "Basic workplace sanitation mandate completely inverted."),
            ("Workplaces must provide clean drinking water and separate toilet facilities for men and women.", 9.6, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Occupational Safety Code 2020, Section 43",
        "clause": "Women may be employed in the establishment for all types of work, and they may also be employed, with their consent, before 6 a.m. and beyond 7 p.m. subject to such conditions relating to safety, holidays and working hours or any other condition to be observed by the employer.",
        "simplified_preserved": "Women can work night shifts between 7 PM and 6 AM, provided they give prior consent and the employer guarantees safe transportation and security.",
        "perturbations": [
            ("Women working after 7 PM must be arrested and sentenced to hard labor.", 1.1, "Not Preserved", "contradiction", "Night work protection turned into criminal penalty."),
            ("Women may work night shifts with their consent and employer safety arrangements.", 9.5, "Preserved", "none", "Accurate plain summary.")
        ]
    },
    {
        "source": "Industrial Disputes Act 1947, Section 33C(2)",
        "clause": "Where any workman is entitled to receive from the employer any money or any benefit which is capable of being computed in terms of money, the workman may make an application to the Labour Court for recovery of the same.",
        "simplified_preserved": "If an employer refuses to pay rightful wages or financial dues, the worker can apply directly to the Labour Court to legally recover the money.",
        "perturbations": [
            ("Workers who file cases in Labour Court to recover unpaid salary are permanently barred from Indian civil life.", 1.1, "Not Preserved", "contradiction", "Statutory recovery remedy inverted into civil death."),
            ("Workers can apply to the Labour Court to recover unpaid money or financial benefits from employers.", 9.5, "Preserved", "none", "Faithful plain restatement.")
        ]
    },
    {
        "source": "Trade Unions Act 1926, Section 18(1)",
        "clause": "No suit or other legal proceeding shall be maintainable in any Civil Court against any registered Trade Union in respect of any act done in contemplation or furtherance of a trade dispute.",
        "simplified_preserved": "Registered trade unions and union officers have statutory legal immunity from civil lawsuits for organizing lawful strikes or labor dispute actions.",
        "perturbations": [
            ("Factory owners can sue individual trade union leaders for ten billion dollars for peaceful strikes.", 1.2, "Not Preserved", "contradiction", "Trade union civil immunity completely negated."),
            ("Registered trade unions have civil immunity for lawful acts done in furtherance of a trade dispute.", 9.5, "Preserved", "none", "Direct plain statement.")
        ]
    },
    {
        "source": "Code on Wages 2019, Section 4",
        "clause": "No employer shall, for the purpose of complying with the provisions of section 3, reduce the rate of wages of any employee, nor shall any employer make any discrimination on the ground of sex in recruitment for the same work or work of a similar nature.",
        "simplified_preserved": "Employers cannot reduce any worker's wages to comply with gender equality laws, nor can they discriminate against women in hiring for identical or similar jobs.",
        "perturbations": [
            ("Employers are legally required to cut all female workers' salaries by 80 percent upon hiring.", 1.1, "Not Preserved", "contradiction", "Equal recruitment and wage protection inverted into discriminatory cut."),
            ("Employers cannot reduce wages or discriminate by gender in recruitment for similar work.", 9.5, "Preserved", "none", "Accurate plain summary.")
        ]
    }
]

EXTRA_LABOR_STATUTORY_HI = [
    {
        "source": "उपदान संदाय अधिनियम 1972, धारा 7(3)",
        "clause": "नियोजक उपदान की राशि उस व्यक्ति को, जिसे वह देय है, उस तारीख से तीस दिन के भीतर संदत्त करने की व्यवस्था करेगा जिस तारीख को वह देय होती है।",
        "simplified_preserved": "मालिक को कर्मचारी के रिटायर होने या नौकरी छोड़ने पर देय ग्रेच्युटी की पूरी राशि 30 दिनों के भीतर चुकानी अनिवार्य है।",
        "perturbations": [
            ("मालिक को ग्रेच्युटी का भुगतान 25 साल तक रोकने की पूरी कानूनी छूट है।", 1.2, "Not Preserved", "date_number", "30 दिन की सीमा को 25 साल किया गया।"),
            ("ग्रेच्युटी देय होने की तारीख से तीस दिनों के भीतर संदत्त की जाएगी।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "मातृत्व प्रसुविधा अधिनियम 1961, धारा 12(1)",
        "clause": "जब कोई स्त्री इस अधिनियम के उपबंधों के अनुसार कार्य से अनुपस्थित रहती है, तो उसके नियोजक के लिए ऐसी अनुपस्थिति के दौरान या उसके कारण उसे पदच्युत या सेवामुक्त करना विधि-विरुद्ध होगा।",
        "simplified_preserved": "मातृत्व अवकाश (मैटर्निटी लीव) पर रहने के दौरान या उसके कारण किसी भी महिला कर्मचारी को नौकरी से निकालना पूरी तरह गैर-कानूनी है।",
        "perturbations": [
            ("मातृत्व अवकाश की अर्जी देते ही महिला कर्मचारी को तत्काल बर्खास्त करना कानूनी कर्तव्य होगा।", 1.1, "Not Preserved", "contradiction", "सुरक्षा का सीधा विलोम।"),
            ("मातृत्व अवकाश के दौरान या उसके कारण महिला को नौकरी से निकालना विधि-विरुद्ध है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "कर्मचारी भविष्य निधि अधिनियम 1952, धारा 14(1)",
        "clause": "जो कोई इस अधिनियम के अधीन अपने द्वारा किए जाने वाले किसी संदाय से बचने के प्रयोजन से जानबूझकर कोई मिथ्या कथन करेगा, वह एक वर्ष तक के कारावास या चार हजार रुपये तक के जुर्माने से दंडनीय होगा।",
        "simplified_preserved": "भविष्य निधि (PF) के भुगतान से बचने के लिए झूठे बयान या दस्तावेज देने पर एक साल तक की जेल या 4,000 रुपये तक का जुर्माना हो सकता है।",
        "perturbations": [
            ("कर्मचारियों का पीएफ हड़पने वाले फर्जीवाड़े पर सरकार की ओर से विशेष नकद पुरस्कार दिया जाएगा।", 1.1, "Not Preserved", "contradiction", "आपराधिक दंड को सरकारी पुरस्कार में बदला गया।"),
            ("पीएफ संदाय से बचने हेतु झूठा बयान देने पर एक वर्ष तक की जेल या जुर्माना हो सकता है।", 9.4, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "कर्मचारी प्रतिकर अधिनियम 1923, धारा 4(1)",
        "clause": "जहां क्षति के परिणामस्वरूप मृत्यु हो जाती है, वहां प्रतिकर की राशि मृत कर्मचारी की मासिक मजदूरी के पचास प्रतिशत के समतुल्य राशि होगी जिसे सुसंगत गुणक से गुणा किया जाएगा।",
        "simplified_preserved": "काम के दौरान हादसे में मजदूर की मौत होने पर उसके परिवार को मासिक वेतन के 50% को कानूनी गुणक से गुणा करके मुआवजा दिया जाएगा।",
        "perturbations": [
            ("मजदूर की मौत होने पर उसके परिवार से फैक्ट्री की सफाई का हर्जाना वसूला जाएगा।", 1.1, "Not Preserved", "entity", "मुआवजा दायित्व का उलटफेर।"),
            ("कार्यस्थल पर मृत्यु होने पर मासिक मजदूरी के 50 प्रतिशत को विहित गुणक से गुणा कर प्रतिकर दिया जाएगा।", 9.4, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "औद्योगिक संबंध संहिता 2020, धारा 62(1)",
        "clause": "औद्योगिक स्थापन में नियोजित कोई भी व्यक्ति नियोजक को हड़ताल की सूचना दिए बिना, हड़ताल करने से पूर्व साठ दिन के भीतर या ऐसी सूचना देने के चौदह दिन के भीतर हड़ताल पर नहीं जाएगा।",
        "simplified_preserved": "औद्योगिक कर्मचारी बिना मालिक को कम से कम 14 दिन पहले लिखित नोटिस दिए हड़ताल पर नहीं जा सकते।",
        "perturbations": [
            ("कर्मचारियों को बिना किसी नोटिस के कभी भी अचानक हड़ताल पर जाने की पूरी कानूनी छूट है।", 1.2, "Not Preserved", "condition", "14 दिन के अनिवार्य हड़ताल नोटिस का लोप।"),
            ("हड़ताल पर जाने से पहले नियोजक को कम से कम 14 दिन पूर्व सूचना देना अनिवार्य है।", 9.4, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "औद्योगिक संबंध संहिता 2020, धारा 67",
        "clause": "जब किसी कर्मकार की जबरी छुट्टी (ले-ऑफ) की जाती है, तो उसे नियोजक द्वारा उन सभी दिनों के लिए प्रतिकर संदत्त किया जाएगा जो मूल मजदूरी और महंगाई भत्ते के पचास प्रतिशत के बराबर होगा।",
        "simplified_preserved": "ले-ऑफ (जबरी छुट्टी) किए जाने पर मजदूर को उसके मूल वेतन और महंगाई भत्ते का 50 प्रतिशत मुआवजा पाना कानूनन अनिवार्य है।",
        "perturbations": [
            ("ले-ऑफ किए गए मजदूर को कोई भी मुआवजा नहीं दिया जाएगा और उसका पिछला वेतन भी जब्त होगा।", 1.1, "Not Preserved", "contradiction", "50% ले-ऑफ मुआवजे का सीधा विलोम।"),
            ("ले-ऑफ के दिनों के लिए मूल वेतन व महंगाई भत्ते का 50 प्रतिशत प्रतिकर देय होगा।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "औद्योगिक संबंध संहिता 2020, धारा 86",
        "clause": "कोई भी नियोजक या कर्मकार या व्यापार संघ, चाहे इस संहिता के अधीन रजिस्ट्रीकृत हो या न हो, कोई अनुचित श्रम व्यवहार नहीं करेगा।",
        "simplified_preserved": "मालिक, मजदूर अथवा ट्रेड यूनियन में से किसी को भी कानून द्वारा निषिद्ध अनुचित श्रम व्यवहार (अन्यायपूर्ण तरीके) अपनाने की अनुमति नहीं है।",
        "perturbations": [
            ("कंपनियों को यूनियनों को कुचलने के लिए अवैध और अनुचित श्रम व्यवहार करने का कानूनी अधिकार है।", 1.1, "Not Preserved", "contradiction", "अनुचित श्रम व्यवहार पर रोक का विलोम।"),
            ("नियोजक या कर्मकार द्वारा अनुचित श्रम व्यवहार करना कानूनन निषिद्ध है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "कारखाना अधिनियम 1948, धारा 16(1)",
        "clause": "किसी कारखाने के किसी कक्ष में उसमें नियोजित श्रमिकों के स्वास्थ्य के लिए हानिकर सीमा तक भीड़ नहीं होगी और प्रत्येक श्रमिक के लिए कम से कम 14.2 घन मीटर स्थान का उपबंध किया जाएगा।",
        "simplified_preserved": "कारखाने के कमरों में खतरनाक भीड़ नहीं होनी चाहिए और प्रत्येक मजदूर के लिए कम से कम 14.2 घन मीटर हवादार जगह होना अनिवार्य है।",
        "perturbations": [
            ("कारखाने में प्रति मजदूर केवल 0.1 घन मीटर स्थान देना ही अनिवार्य होगा ताकि अधिक मजदूर भरे जा सकें।", 1.2, "Not Preserved", "date_number", "14.2 घन मीटर की स्वास्थ्य सीमा का उल्लंघन।"),
            ("कारखाने में अत्यधिक भीड़ नहीं होगी और प्रति श्रमिक कम से कम 14.2 घन मीटर स्थान होगा।", 9.4, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "कारखाना अधिनियम 1948, धारा 21(1)",
        "clause": "प्रत्येक कारखाने में मशीनरी के प्रत्येक खतरनाक भाग को मजबूत संनिर्माण के संरक्षकों द्वारा सुरक्षित रूप से बाड़ लगाया जाएगा और जब मशीन चालू हो तो उसे सुरक्षित रखा जाएगा।",
        "simplified_preserved": "कारखाने की सभी खतरनाक मशीनों के चारों ओर मजबूत सुरक्षा जाली (बाड़) लगाना अनिवार्य है ताकि चालू हालत में कोई हादसा न हो।",
        "perturbations": [
            ("मजदूरों को चालू आरी और कटर पर बिना किसी सुरक्षा घेरे के काम करने को मजबूर किया जाएगा।", 1.1, "Not Preserved", "contradiction", "सुरक्षा बाड़ की अनिवार्यता का विलोम।"),
            ("खतरनाक मशीनरी के पुर्जों पर मजबूत सुरक्षा बाड़ लगाना अनिवार्य है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "कारखाना अधिनियम 1948, धारा 67",
        "clause": "कोई भी बालक जिसने अपनी चौदह वर्ष की आयु पूरी नहीं की है, किसी कारखाने में कार्य करने के लिए न तो अपेक्षित किया जाएगा और न ही उसे अनुज्ञात किया जाएगा।",
        "simplified_preserved": "14 वर्ष से कम उम्र के किसी भी बच्चे से किसी कारखाने में काम कराना कानूनन पूरी तरह प्रतिबंधित है।",
        "perturbations": [
            ("पांच वर्ष के बच्चों को कारखानों में 18 घंटे काम पर लगाना अनिवार्य किया गया है।", 1.1, "Not Preserved", "contradiction", "बाल श्रम निषेध का सीधा विलोम।"),
            ("चौदह वर्ष से कम आयु के बालक को किसी कारखाने में काम करने की अनुमति नहीं होगी।", 9.6, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "कारखाना अधिनियम 1948, धारा 79(1)",
        "clause": "प्रत्येक श्रमिक जिसने किसी कैलेण्डर वर्ष में 240 दिन या उससे अधिक कार्य किया है, उसे आगामी वर्ष में प्रत्येक बीस दिन के कार्य पर एक दिन की दर से मजदूरी सहित छुट्टी दी जाएगी।",
        "simplified_preserved": "साल में 240 दिन काम करने वाले कारखाने के मजदूर को हर 20 दिन के काम के बदले 1 दिन की सवेतन (सैलरी वाली) छुट्टी पाने का कानूनी हक है।",
        "perturbations": [
            ("साल भर काम करने वाले मजदूर को छुट्टी मांगने पर वेतन काटकर निकाल दिया जाएगा।", 1.2, "Not Preserved", "contradiction", "सवेतन छुट्टी के अधिकार का खंडन।"),
            ("वर्ष में 240 दिन काम करने पर प्रत्येक 20 दिन के कार्य हेतु एक दिन की सवेतन छुट्टी मिलेगी।", 9.4, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 14",
        "clause": "सहमति तब स्वतंत्र कही जाती है जब वह प्रपीड़न, असम्यक असर, कपट, दुर्व्यपदेशन या भूल से कारित न हुई हो।",
        "simplified_preserved": "अनुबंध में सहमति तभी कानूनी रूप से स्वतंत्र मानी जाती है जब वह धमकी, दबाव, धोखे, झूठे वादे या गलतफहमी के बिना दी गई हो।",
        "perturbations": [
            ("बंदूक की नोक पर और जान से मारने की धमकी देकर ली गई सहमति पूरी तरह स्वतंत्र मानी जाएगी।", 1.1, "Not Preserved", "contradiction", "स्वतंत्र सहमति की परिभाषा का सीधा विलोम।"),
            ("प्रपीड़न, असम्यक असर, कपट या भूल से रहित सहमति स्वतंत्र कहलाती है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 15",
        "clause": "प्रपीड़न भारतीय दंड संहिता द्वारा निषिद्ध किसी कार्य को करने या करने की धमकी देने या किसी संपत्ति को विधि-विरुद्ध निरुद्ध करने को कहते हैं जिसका उद्देश्य किसी व्यक्ति से करार कराना हो।",
        "simplified_preserved": "प्रपीड़न (कोअर्सन) का मतलब किसी को समझौता करने पर मजबूर करने के लिए कानूनी रूप से प्रतिबंधित अपराध करना, धमकी देना या उसकी संपत्ति पर अवैध कब्जा करना है।",
        "perturbations": [
            ("प्रपीड़न को अनुबंध कराने का सबसे वैध और सर्वोत्तम कानूनी तरीका माना गया है।", 1.1, "Not Preserved", "contradiction", "प्रपीड़न को वैध ठहराना।"),
            ("अपराध करने की धमकी या संपत्ति का अवैध निरोध प्रपीड़न कहलाता है।", 9.4, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 16(1)",
        "clause": "संविदा असम्यक असर द्वारा उत्प्रेरित तब कही जाती है जब पक्षकारों के बीच संबंध ऐसे हों कि एक पक्षकार दूसरे की इच्छा को अधिशासित करने की स्थिति में हो और अनुचित लाभ प्राप्त करने के लिए उसका उपयोग करे।",
        "simplified_preserved": "असम्यक असर (अनड्यू इन्फ्लुएंस) तब होता है जब एक प्रभावशाली व्यक्ति दूसरे पर अपने रसूख या अधिकार का दुरुपयोग करके अनुचित कानूनी फायदा उठाता है।",
        "perturbations": [
            ("बाजार में दो अनजान व्यापारियों द्वारा निष्पक्ष बोली लगाना असम्यक असर कहलाता है।", 1.5, "Not Preserved", "scope", "असम्यक असर का सामान्य सौदे में गलत विस्तार।"),
            ("दूसरे की इच्छा को प्रभावित करने की स्थिति का अनुचित लाभ उठाना असम्यक असर है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 17",
        "clause": "कपट से तात्पर्य किसी ऐसे तथ्य का जो सत्य नहीं है, ऐसे व्यक्ति द्वारा सुझाया जाना है जो उसके सत्य होने का विश्वास नहीं करता, या किसी तथ्य का सक्रिय रूप से छिपाया जाना है जिससे दूसरे को धोखा दिया जा सके।",
        "simplified_preserved": "कपट (धोखाधड़ी) का अर्थ जानबूझकर झूठी बात कहना या जानबूझकर सच छिपाना है ताकि सामने वाले को झांसे में लेकर समझौता कराया जा सके।",
        "perturbations": [
            ("कपट का अर्थ है पूरी सच्चाई से काम करना और ग्राहक को सब कुछ स्पष्ट बता देना।", 1.1, "Not Preserved", "contradiction", "कपट की परिभाषा का सीधा विलोम।"),
            ("धोखा देने के इरादे से झूठी बात कहना या तथ्य छिपाना कपट है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 18",
        "clause": "दुर्व्यपदेशन से तात्पर्य किसी असत्य बात का ऐसा सकारात्मक प्रकथन है जो उस व्यक्ति की जानकारी से समर्थित न हो, यद्यपि वह उसे सत्य मानता हो, और जिससे दूसरे पक्षकार को भूल में डाला जाए।",
        "simplified_preserved": "दुर्व्यपदेशन (मिसरेप्रजेंटेशन) का मतलब बिना पुख्ता आधार के ऐसी गलत बात कहना है जिसे कहने वाला सच मानता हो, परंतु जिससे सामने वाला गुमराह होकर अनुबंध कर ले।",
        "perturbations": [
            ("दुर्व्यपदेशन का अर्थ है वैज्ञानिक रूप से सिद्ध शत-प्रतिशत सत्य बातें बोलना।", 1.1, "Not Preserved", "contradiction", "दुर्व्यपदेशन का विलोम।"),
            ("बिना आधार के गलत बात कहना जिससे दूसरा पक्षकार गुमराह हो, दुर्व्यपदेशन कहलाता है।", 9.4, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 23",
        "clause": "करार का प्रतिफल या उद्देश्य विधिपूर्ण है, जब तक कि वह विधि द्वारा निषिद्ध न हो, या किसी विधि के उपबंधों को विफल करने वाला न हो, या कपटपूर्ण न हो, या किसी अन्य के शरीर या संपत्ति को क्षति पहुंचाने वाला न हो, अथवा न्यायालय उसे अनैतिक या लोक नीति के विरुद्ध न समझे।",
        "simplified_preserved": "किसी भी समझौते का उद्देश्य व लेन-देन तभी कानूनी होता है जब वह कानून के खिलाफ न हो, कपटपूर्ण न हो, किसी को नुकसान न पहुंचाए और लोकनीति के विरुद्ध न हो।",
        "perturbations": [
            ("सुपारी लेकर हत्या करने और दंगे भड़काने के करार पूरी तरह विधिपूर्ण और मान्य माने जाएंगे।", 1.1, "Not Preserved", "contradiction", "विधि विरुद्ध उद्देश्य का सीधा विलोम।"),
            ("प्रतिफल या उद्देश्य विधिपूर्ण है जब तक वह गैर-कानूनी, कपटपूर्ण, हानिकारक या अनैतिक न हो।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 25",
        "clause": "बिना प्रतिफल के किया गया करार शून्य है, जब तक कि वह लिखित और पंजीकृत न हो तथा एक-दूसरे के निकट संबंधी पक्षकारों के बीच नैसर्गिक प्रेम और स्नेह के कारण न किया गया हो।",
        "simplified_preserved": "बिना लेन-देन (प्रतिफल) का कोई भी समझौता कानूनन शून्य (अमान्य) होता है, सिवाय तब जब वह करीबी परिजनों के बीच प्रेमवश लिखित व रजिस्टर्ड रूप में किया गया हो।",
        "perturbations": [
            ("अनजान लोगों के बीच बिना किसी पैसे या सामान के किया गया हर मौखिक वादा पूर्णतः वैध अनुबंध होगा।", 1.2, "Not Preserved", "contradiction", "बिना प्रतिफल शून्य करार के नियम का विलोम।"),
            ("बिना प्रतिफल के करार शून्य है, जब तक कि वह निकट संबंधियों के बीच लिखित व पंजीकृत न हो।", 9.4, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 29",
        "clause": "वे करार जिनका अर्थ निश्चित नहीं है, या निश्चित किए जाने योग्य नहीं है, शून्य हैं।",
        "simplified_preserved": "ऐसे सभी समझौते जिनकी शर्तें अस्पष्ट, अनिश्चित या समझ से परे हों, कानूनन शून्य (अमान्य) होते हैं।",
        "perturbations": [
            ("अस्पष्ट और निरर्थक शब्दों वाले समझौतों को अदालतें सबसे सख्ती से लागू करेंगी।", 1.1, "Not Preserved", "contradiction", "अनिश्चितता के नियम का विलोम।"),
            ("जिन करारों का अर्थ निश्चित नहीं किया जा सकता, वे शून्य होते हैं।", 9.6, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 30",
        "clause": "दांव (बाजी) के तौर पर किए गए करार शून्य हैं; और किसी दांव पर जीती हुई किसी चीज को वसूलने के लिए कोई वाद नहीं लाया जा सकेगा।",
        "simplified_preserved": "सट्टेबाजी और जुए के सभी समझौते गैर-कानूनी व शून्य होते हैं, और सट्टे की रकम वसूलने के लिए अदालत में कोई मुकदमा नहीं चलाया जा सकता।",
        "perturbations": [
            ("हाईकोर्ट का मुख्य कर्तव्य जुआरियों के सट्टे की हारी-जीती रकम की वसूली करवाना होगा।", 1.1, "Not Preserved", "contradiction", "बाजी के करार की शून्यता का विलोम।"),
            ("बाजी (दांव) के तौर पर किए गए करार शून्य हैं और जीती रकम हेतु मुकदमा नहीं लाया जा सकता।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 39",
        "clause": "जब संविदा के किसी पक्षकार ने अपने वचन का पूर्णतः पालन करने से इनकार कर दिया हो, तो वचनग्रहीता संविदा का अंत कर सकेगा।",
        "simplified_preserved": "यदि कोई पक्षकार अपने वादे का पालन करने से साफ मना कर दे, तो दूसरा पक्षकार उस अनुबंध को तत्काल समाप्त कर सकता है।",
        "perturbations": [
            ("ठेकेदार द्वारा काम करने से साफ मना करने पर भी ग्राहक जीवन भर उसे बिना काम के पैसे देने के लिए बाध्य रहेगा।", 1.2, "Not Preserved", "contradiction", "संविदा अंत करने के अधिकार का खंडन।"),
            ("जब कोई पक्षकार वचन पालन से इनकार कर दे, तो दूसरा पक्षकार संविदा समाप्त कर सकता है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 62",
        "clause": "यदि संविदा के पक्षकार उसके स्थान पर नई संविदा प्रतिस्थापित करने, या उसे विखंडित या परिवर्तित करने का करार करते हैं, तो मूल संविदा का पालन करने की आवश्यकता नहीं है।",
        "simplified_preserved": "जब दोनों पक्ष आपस में मिलकर पुराना अनुबंध बदलकर नया बना लें, तो उन्हें मूल (पुराने) अनुबंध का पालन करने की कोई जरूरत नहीं रहती।",
        "perturbations": [
            ("नया अनुबंध बन जाने के बाद भी पुराने रद्द अनुबंध का पालन करना अनिवार्य बना रहेगा।", 1.2, "Not Preserved", "contradiction", "नवीयन (नोवेशन) के विधिक नियम का विलोम।"),
            ("पक्षकारों द्वारा नई संविदा प्रतिस्थापित करने पर मूल संविदा का पालन आवश्यक नहीं रहता।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 65",
        "clause": "जब कोई करार शून्य पाया जाता है, या जब कोई संविदा शून्य हो जाती है, तो जो कोई व्यक्ति ऐसे करार या संविदा के अधीन कोई फायदा प्राप्त कर चुका है, वह उसे लौटाने या प्रतिकर देने के लिए आबद्ध है।",
        "simplified_preserved": "यदि कोई समझौता गैर-कानूनी या शून्य घोषित हो जाए, तो उसके तहत लिया गया कोई भी लाभ या अग्रिम राशि मूल मालिक को वापस लौटानी होगी।",
        "perturbations": [
            ("शून्य करार के तहत मिला सारा पैसा हड़पने और दबा लेने की कानूनन पूरी छूट होगी।", 1.1, "Not Preserved", "contradiction", "प्रत्यास्थापन (रेस्टिट्यूशन) के दायित्व का विलोम।"),
            ("करार शून्य होने पर उससे प्राप्त फायदा लौटाना या उसके बदले प्रतिकर देना अनिवार्य है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 172",
        "clause": "किसी ऋण के संदाय के लिए या किसी वचन के पालन के लिए प्रतिभूति के तौर पर माल का उपनिधान गिरवी कहलाता है। उपनिधाता इस दशा में गिरवीकर्ता कहलाता है और उपनिहिती गिरवीदार कहलाता है।",
        "simplified_preserved": "कर्ज चुकाने या वादा निभाने की गारंटी के तौर पर सामान या जेवर गिरवी रखना (प्लेज) कहलाता है।",
        "perturbations": [
            ("गिरवी का अर्थ है कि बैंक ग्राहक का सोना लेकर हमेशा के लिए बिना कर्ज दिए भाग सकता है।", 1.2, "Not Preserved", "contradiction", "गिरवी की विधिक प्रतिभूति परिभाषा का उलटफेर।"),
            ("ऋण के संदाय हेतु प्रतिभूति के तौर पर माल सौंपना गिरवी कहलाता है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "भारतीय संविदा अधिनियम 1872, धारा 182",
        "clause": "अभिकर्ता (एजेंट) वह व्यक्ति है जो किसी अन्य की ओर से कोई कार्य करने के लिए अथवा पर-व्यक्तियों के साथ व्यवहारों में किसी अन्य का प्रतिनिधित्व करने के लिए नियोजित किया गया है। जिसकी ओर से ऐसा कार्य किया जाता है, उसे मालिक (प्रिंसिपल) कहा जाता है।",
        "simplified_preserved": "एजेंट वह व्यक्ति है जिसे किसी अन्य व्यक्ति (मालिक) की ओर से काम करने या तीसरे पक्ष के साथ सौदों में उसका प्रतिनिधित्व करने का कानूनी अधिकार दिया गया हो।",
        "perturbations": [
            ("एजेंट को अपने मालिक का प्रतिनिधित्व करने या उसकी ओर से बोलने का कोई कानूनी हक नहीं होता।", 1.2, "Not Preserved", "contradiction", "अभिकरण (एजेंसी) की परिभाषा का सीधा विलोम।"),
            ("मालिक की ओर से कार्य करने या प्रतिनिधित्व करने वाला व्यक्ति अभिकर्ता कहलाता है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "सामाजिक सुरक्षा संहिता 2020, धारा 114(1)",
        "clause": "प्रत्येक एग्रीगेटर गिग कर्मकारों और प्लेटफॉर्म कर्मकारों के सामाजिक सुरक्षा कोष में ऐसी दर पर अंशदान करेगा जो ऐसे प्रत्येक एग्रीगेटर के वार्षिक आवर्त (टर्नओवर) के दो प्रतिशत से अधिक नहीं होगी, किंतु एक प्रतिशत से कम नहीं होगी।",
        "simplified_preserved": "ऑनलाइन डिलीवरी व कैब कंपनियों (एग्रीगेटर्स) को गिग व डिलीवरी कर्मचारियों के कल्याण कोष में अपने सालाना टर्नओवर का 1 से 2 प्रतिशत अंशदान देना अनिवार्य है।",
        "perturbations": [
            ("कंपनियों को गिग कामगारों के लिए कोई भी कल्याण कोष देने की सख्त मनाही होगी।", 1.1, "Not Preserved", "contradiction", "सामाजिक सुरक्षा अंशदान दायित्व का विलोम।"),
            ("एग्रीगेटर्स को वार्षिक टर्नओवर का 1 से 2 प्रतिशत गिग कर्मकार कोष में देना अनिवार्य है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "उपजीविकाजन्य सुरक्षा संहिता 2020, धारा 32(1)",
        "clause": "प्रत्येक स्थापन में शुद्ध पेय जल का पर्याप्त प्रदाय और पुरुष तथा महिला श्रमिकों के लिए पृथक विहित प्रकार के शौचालय की व्यवस्था की जाएगी और उसे बनाए रखा जाएगा।",
        "simplified_preserved": "हर कार्यस्थल और फैक्ट्री में साफ पीने का पानी और महिला व पुरुष कर्मचारियों के लिए अलग, स्वच्छ शौचालयों की व्यवस्था करना कानूनी रूप से अनिवार्य है।",
        "perturbations": [
            ("मालिकों को कारखानों से पीने का पानी और शौचालय की सुविधा पूरी तरह बंद करने की कानूनी छूट होगी।", 1.1, "Not Preserved", "contradiction", "स्वच्छता व पेयजल अनिवार्यता का विलोम।"),
            ("कार्यस्थल पर शुद्ध पेयजल और महिला-पुरुष हेतु पृथक शौचालयों की व्यवस्था अनिवार्य है।", 9.6, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "उपजीविकाजन्य सुरक्षा संहिता 2020, धारा 43",
        "clause": "महिलाएं किसी भी प्रकार के कार्य के लिए स्थापन में नियोजित की जा सकेंगी, और उनकी सहमति से उन्हें प्रातः 6 बजे से पूर्व तथा सायं 7 बजे के पश्चात् भी सुरक्षा, अवकाश तथा कार्य के घंटों संबंधी शर्तों के अधीन नियोजित किया जा सकेगा।",
        "simplified_preserved": "महिला कर्मचारी अपनी लिखित सहमति और सुरक्षित यात्रा व माहौल की कानूनी शर्तों के अधीन शाम 7 बजे से सुबह 6 बजे की नाइट शिफ्ट में काम कर सकती हैं।",
        "perturbations": [
            ("रात में काम करने वाली महिलाओं को तत्काल जेल भेजकर कठिन कारावास दिया जाएगा।", 1.1, "Not Preserved", "contradiction", "रात्रि कार्य की विधिक अनुमति का विलोम।"),
            ("सहमति और सुरक्षा शर्तों के अधीन महिलाओं को रात्रि कार्य में नियोजित किया जा सकता है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "औद्योगिक विवाद अधिनियम 1947, धारा 33C(2)",
        "clause": "जहां कोई कर्मकार नियोजक से कोई धन या कोई ऐसा फायदा प्राप्त करने का हकदार है जो धन के रूप में परिकलित किया जा सकता है, वहां कर्मकार उसकी वसूली के लिए श्रम न्यायालय को आवेदन कर सकेगा।",
        "simplified_preserved": "यदि मालिक बकाया वेतन या कानूनी लाभ देने से मना करे, तो मजदूर सीधे श्रम न्यायालय (लेबर कोर्ट) में आवेदन देकर अपना पैसा वसूल करवा सकता है।",
        "perturbations": [
            ("बकाया वेतन मांगने वाले मजदूर को आजीवन जेल में डालकर उसका सारा पिछला वेतन जब्त कर लिया जाएगा।", 1.1, "Not Preserved", "contradiction", "विधिक वसूली के अधिकार का विलोम।"),
            ("कर्मकार नियोजक से देय धन की वसूली हेतु श्रम न्यायालय में आवेदन कर सकता है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "व्यापार संघ अधिनियम 1926, धारा 18(1)",
        "clause": "किसी रजिस्ट्रीकृत व्यापार संघ के विरुद्ध किसी व्यापार विवाद को आगे बढ़ाने के लिए किए गए किसी कार्य की बाबत किसी सिविल न्यायालय में कोई वाद या अन्य विधिक कार्यवाही पोषणीय नहीं होगी।",
        "simplified_preserved": "वैध औद्योगिक विवाद में शामिल होने या शांतिपूर्ण हड़ताल करने के लिए पंजीकृत ट्रेड यूनियन और उसके नेताओं पर दीवानी मुकदमा (हर्जाने का केस) नहीं चलाया जा सकता।",
        "perturbations": [
            ("फैक्ट्री मालिक हड़ताल करने वाले यूनियन नेताओं की निजी संपत्तियों पर तत्काल कब्जा करने के हकदार होंगे।", 1.2, "Not Preserved", "contradiction", "सिविल उन्मुक्ति का सीधा उलटफेर।"),
            ("व्यापार विवाद में किए गए कार्यों हेतु रजिस्ट्रीकृत ट्रेड यूनियन को सिविल वाद से विधिक उन्मुक्ति प्राप्त है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    },
    {
        "source": "मजदूरी संहिता 2019, धारा 4",
        "clause": "कोई भी नियोजक किसी कर्मचारी की मजदूरी की दर कम नहीं करेगा, और न ही समरूप प्रकृति के कार्य के लिए भर्ती में लिंग के आधार पर कोई भेदभाव करेगा।",
        "simplified_preserved": "मालिक महिला कर्मचारियों की भर्ती में कोई भेदभाव नहीं कर सकता और न ही समान काम के लिए किसी भी कर्मचारी का वेतन कम कर सकता है।",
        "perturbations": [
            ("मालिकों को महिलाओं को पुरुषों से 90 प्रतिशत कम वेतन देकर ही भर्ती करने का अनिवार्य आदेश है।", 1.1, "Not Preserved", "contradiction", "समान भर्ती व पारिश्रमिक संरक्षण का विलोम।"),
            ("समान कार्य हेतु भर्ती में लिंग आधारित भेदभाव और वेतन में कटौती पूर्णतः प्रतिबंधित है।", 9.5, "Preserved", "none", "सटीक विधिक रूप।")
        ]
    }
]
