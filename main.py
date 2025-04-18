import streamlit as st
import pandas as pd
from datetime import datetime
import re

# Set page configuration
st.set_page_config(page_title="CAS Decision Search", layout="wide")

# Basic styling - clean and simple
st.markdown("""
<style>
    body {font-family: Arial, sans-serif;}
    
    /* Simple header */
    .header {
        padding: 1rem 0;
        border-bottom: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    /* Clean search container */
    .search-container {
        margin-bottom: 1.5rem;
    }
    
    /* Results container */
    .results-container {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Case title */
    .case-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    /* Case metadata */
    .case-meta {
        font-size: 0.9rem;
        color: #6b7280;
        margin-bottom: 0.75rem;
    }
    
    /* Highlight chunk */
    .highlight-chunk {
        background-color: #dcfce7;
        padding: 1rem;
        border-left: 4px solid #10b981;
        margin-bottom: 0.75rem;
        border-radius: 4px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }
    
        /* Relevance explanation - emphasized with blue background */
    .relevance {
        font-size: 0.95rem;
        color: #1f2937;
        background-color: #e6f0f9;
        border: 1px solid #3b82f6;
        border-left: 4px solid #3b82f6;
        padding: 0.75rem;
        border-radius: 4px;
        margin-bottom: 1.5rem;
        font-weight: 500;
    }
    
    /* Simple button */
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border: none;
    }
    
    /* Remove excess padding */
    .stTextInput>div>div>input {
        padding: 0.5rem;
    }
    
    /* History item */
    .history-item {
        padding: 0.5rem;
        border-bottom: 1px solid #f3f4f6;
    }
    
    /* Make sidebar cleaner */
    section[data-testid="stSidebar"] > div {
        background-color: #f9fafb;
        padding: 1.5rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sample CAS decision content with longer text chunks for highlighting
cas_decisions = [
    {
        "id": "CAS 2020/A/6978",
        "title": "Football Club Atlético Madrid v. FIFA",
        "date": "2020-10-18",
        "type": "Appeal",
        "sport": "Football",
        "full_text": """
1. The Appellant, Football Club Atlético Madrid (the "Club" or the "Appellant"), is a professional football club with its registered office in Madrid, Spain. The Club is a member of the Royal Spanish Football Federation (the "RFEF"), which in turn is affiliated to the Fédération Internationale de Football Association.

2. The Respondent, Fédération Internationale de Football Association (the "Respondent" or "FIFA"), is the world governing body of football. It exercises regulatory, supervisory and disciplinary functions over national associations, clubs, officials and players worldwide. FIFA has its registered office in Zurich, Switzerland.

3. On 31 January 2019, the Club signed an employment contract with the player Diego Costa (the "Player"), valid until 30 June 2023 (the "Employment Contract").

4. According to Clause 8 of the Employment Contract, in the event that the Player unilaterally terminates the Employment Contract without just cause, he would have to pay to the Club compensation in the amount of EUR 30,000,000 (the "Buy-out Clause").

5. On 8 July 2020, the Player informed the Club via his legal representatives that he wished to terminate his Employment Contract prematurely and without just cause. The Player's representatives confirmed that the amount of EUR 30,000,000 corresponding to the Buy-out Clause would be deposited with the Spanish Liga Nacional de Fútbol Profesional.

6. On 12 July 2020, Chelsea Football Club ("Chelsea") publicly announced that it had signed the Player.

7. On 15 July 2020, the Club filed a claim with the FIFA Players' Status Committee (the "FIFA PSC") against the Player and Chelsea, requesting jointly and severally from them the amount of EUR 80,000,000 as compensation for breach of contract without just cause by the Player, arguing that the real market value of the Player was significantly higher than the amount of the Buy-out Clause.

8. On 19 January 2021, the Single Judge of the FIFA PSC rendered the following decision (the "Appealed Decision"):

   "1. The claim of the Claimant, Atlético Madrid, is rejected.
   2. The final costs of the proceedings in the amount of CHF 25,000 are to be paid by the Claimant."

9. The Single Judge of the FIFA PSC determined that the Player had validly terminated his Employment Contract in accordance with the terms of the Buy-out Clause and Spanish law. The Single Judge held that the Buy-out Clause was freely agreed upon by the parties and represented a genuine pre-estimate of the compensation due in case of unilateral termination without just cause by the Player. The fact that the market value of the Player might have increased since the conclusion of the Employment Contract did not render the Buy-out Clause invalid or unenforceable.

10. On 9 February 2021, the Club filed a Statement of Appeal with the Court of Arbitration for Sport ("CAS") against the Appealed Decision.

II. PROCEEDINGS BEFORE THE COURT OF ARBITRATION FOR SPORT

11. The Panel holds that Spanish law applies to the assessment of the Buy-out Clause. It is undisputed that the Employment Contract is governed by Spanish law, and the Buy-out Clause is part of that contract.

12. According to Article 16.1 of the Spanish Royal Decree 1006/1985, which regulates the special employment relationship of professional athletes, a professional athlete may unilaterally terminate his/her employment contract, provided that compensation is paid as agreed in the contract or as established by ordinary courts.

13. The Panel notes that the Buy-out Clause was freely negotiated and agreed upon by the Club and the Player. Both parties were represented by counsel and had equal bargaining power at the time of the conclusion of the Employment Contract. The Club, being one of Europe's top football clubs, certainly had the necessary knowledge and experience to properly assess the Player's value and to set the amount of the Buy-out Clause accordingly.

14. The Panel acknowledges that in certain cases, it might be possible to challenge a contractual buy-out clause if it is manifestly disproportionate to the actual damage suffered. However, the burden of proof lies with the party challenging the clause, in this case the Club.

15. The Panel finds that the Club has failed to establish that the amount of EUR 30,000,000 agreed in the Buy-out Clause was manifestly disproportionate to the Player's value at the time when the Employment Contract was concluded. The mere fact that the market value of the Player may have increased since then does not render the Buy-out Clause invalid or unenforceable.

16. The Panel further notes that Spanish courts have consistently upheld buy-out clauses in professional football contracts, provided that they were freely agreed upon by the parties. The Panel sees no reason to depart from this established practice.

17. Therefore, the Panel finds that the Player validly terminated his Employment Contract by paying the amount stipulated in the Buy-out Clause, and neither the Player nor Chelsea owe any additional compensation to the Club.

III. DECISION

The Court of Arbitration for Sport rules that:

1. The appeal filed by Football Club Atlético Madrid on 9 February 2021 against the decision rendered by the Single Judge of the FIFA Players' Status Committee on 19 January 2021 is dismissed.

2. The decision rendered by the Single Judge of the FIFA Players' Status Committee on 19 January 2021 is confirmed.

3. The costs of the arbitration, to be determined and communicated separately by the CAS Court Office, shall be borne by Football Club Atlético Madrid.

4. Football Club Atlético Madrid shall pay to FIFA a total amount of CHF 7,000 (seven thousand Swiss Francs) as contribution towards its legal and other costs incurred in connection with the present proceedings.

5. All other motions or prayers for relief are dismissed.
        """,
        "claimant": "Football Club Atlético Madrid",
        "respondent": "FIFA",
        "panel": "Prof. Ulrich Haas (President), Mr. Efraim Barak, Mr. José Juan Pintó",
        "decision": "Appeal dismissed, FIFA PSC decision confirmed.",
        "keywords": ["buy-out clause", "contract termination", "transfer", "compensation", "Spanish law"]
    },
    {
        "id": "CAS 2021/A/7876",
        "title": "World Anti-Doping Agency (WADA) v. Sun Yang & Fédération Internationale de Natation (FINA)",
        "date": "2021-06-22",
        "type": "Appeal",
        "sport": "Swimming",
        "full_text": """
1. The First Respondent is Mr. Sun Yang (the "Athlete" or the "First Respondent"), a Chinese professional swimmer, born on 1 December 1991. The Athlete is one of China's most successful swimmers. He won gold medals at the Olympic Games in London (2012) and Rio de Janeiro (2016), and has won multiple gold medals at the World Championships.

2. The Second Respondent is the Fédération Internationale de Natation ("FINA" or the "Second Respondent"), the international federation governing the sport of swimming worldwide. FINA has its headquarters in Lausanne, Switzerland.

3. The Appellant is the World Anti-Doping Agency ("WADA" or the "Appellant"), a Swiss private law foundation with its seat in Lausanne, Switzerland, and having its headquarters in Montreal, Canada. WADA was established in 1999 to promote, coordinate, and monitor the fight against doping in sport internationally.

4. On 4 September 2018, a team of three doping control officers (the "DCOs") from International Doping Tests & Management ("IDTM"), a company providing anti-doping services to sports organizations including FINA, arrived at the Athlete's residence to collect blood and urine samples from the Athlete.

5. The Athlete provided a blood sample but then challenged the credentials and authorization of the DCOs. After a telephone call to the Athlete's doctor, who advised the Athlete not to proceed with the test, the Athlete's entourage, including his personal security guard, destroyed the container holding the already-collected blood sample. The Athlete also refused to provide a urine sample.

6. On 6 January 2019, the FINA Doping Panel held a hearing. On 3 January 2019, the FINA Doping Panel issued a decision finding that the sample collection procedure did not comply with the required standards and cleared the Athlete of any wrongdoing (the "FINA Decision").

7. On 14 February 2019, WADA filed a Statement of Appeal with the Court of Arbitration for Sport ("CAS") against the FINA Decision, naming the Athlete and FINA as respondents.

8. A hearing was held on 15 November 2019 in Montreux, Switzerland. On 28 February 2020, the CAS Panel issued its decision sanctioning the Athlete with an eight-year period of ineligibility.

9. On 22 December 2020, the Swiss Federal Tribunal set aside the CAS Award on the ground of bias of one of the arbitrators and referred the case back to the CAS to be reheard by a new panel.

II. MERITS OF THE APPEAL

10. The key issue for determination by the Panel is whether the Athlete committed an anti-doping rule violation ("ADRV") by tampering with the doping control process.

11. Article 2.5 of the FINA Doping Control Rules ("FINA DC") provides that "tampering or attempted tampering with any part of doping control" constitutes an ADRV. "Tampering" is defined in Appendix 1 to the FINA DC as "[a]ltering for an improper purpose or in an improper way; bringing improper influence to bear; interfering improperly; obstructing, misleading or engaging in any fraudulent conduct to alter results or prevent normal procedures from occurring".

12. The Panel finds that the Athlete's actions on 4 September 2018 constituted tampering within the meaning of Article 2.5 of the FINA DC. The Athlete failed to cooperate with the sample collection process, directed his security guard to destroy the blood sample container, and refused to provide a urine sample.

13. The Panel dismisses the Athlete's argument that he was entitled to challenge the DCOs' credentials and authorization. While an athlete has the right to raise concerns about the credentials of DCOs, the appropriate course of action is to proceed with the test and file a complaint afterward, not to take matters into his own hands by destroying the sample container.

14. The Panel finds that the Athlete's conduct was not justified. The DCOs had provided appropriate documentation, including their IDTM authorization letters, IDTM DCO badges, and their national identification cards. Moreover, the Athlete had previously been tested by IDTM DCOs using the same documentation.

15. As to the sanction, the Panel notes that this is the Athlete's second ADRV. Article 10.7.1 of the FINA DC provides that for an athlete's second ADRV, the period of ineligibility shall be "twice the period of ineligibility otherwise applicable to the second anti-doping rule violation treated as if it were a first violation, without taking into account any reduction under Article 10.6".

16. Given that the standard sanction for tampering under Article 10.3.1 of the FINA DC is a four-year period of ineligibility, and considering this is the Athlete's second ADRV, the Panel determines that the appropriate sanction is a period of ineligibility of four years.

17. The Panel determines that the period of ineligibility shall commence on 28 February 2020, the date of the original CAS Award, with credit given for the period of provisional suspension already served by the Athlete.

III. DECISION

The Court of Arbitration for Sport rules that:

1. The appeal filed by the World Anti-Doping Agency on 14 February 2019 against the decision rendered by the FINA Doping Panel on 3 January 2019 is upheld.

2. The decision rendered by the FINA Doping Panel on 3 January 2019 is set aside.

3. Sun Yang is found to have committed a violation of Article 2.5 of the FINA Doping Control Rules.

4. Sun Yang is sanctioned with a period of ineligibility of four (4) years, commencing on 28 February 2020.

5. All competitive results obtained by Sun Yang from 4 September 2018 to 28 February 2020 are disqualified, with all resulting consequences, including forfeiture of any medals, points, and prizes.
        """,
        "claimant": "World Anti-Doping Agency (WADA)",
        "respondent": "Sun Yang & Fédération Internationale de Natation (FINA)",
        "panel": "Prof. Hans Nater (President), Mr. Romano Subiotto QC, Mr. Philippe Sands QC",
        "decision": "Appeal upheld, four-year period of ineligibility imposed.",
        "keywords": ["doping", "tampering", "sample collection", "ineligibility", "second violation"]
    },
    {
        "id": "CAS 2019/A/6298",
        "title": "Manchester City FC v. UEFA",
        "date": "2019-11-15",
        "type": "Appeal",
        "sport": "Football",
        "full_text": """
1. The Appellant, Manchester City Football Club ("MCFC" or the "Club" or the "Appellant"), is a professional football club with its registered office in Manchester, United Kingdom. MCFC competes in the Premier League, the top division of English football, and regularly participates in UEFA club competitions.

2. The Respondent, the Union of European Football Associations ("UEFA" or the "Respondent"), is the governing body of football at the European level. It is an association incorporated under Swiss law with its headquarters in Nyon, Switzerland.

3. On 7 March 2019, the Investigatory Chamber of the UEFA Club Financial Control Body ("CFCB") opened an investigation into MCFC for potential breaches of the UEFA Club Licensing and Financial Fair Play Regulations (the "FFP Regulations").

4. The investigation was initiated following the publication of various articles in the German magazine Der Spiegel in November 2018, which were based on documents and email correspondence allegedly obtained from Football Leaks.

5. On 14 May 2019, the Chief Investigator of the CFCB Investigatory Chamber referred the case to the CFCB Adjudicatory Chamber, recommending that MCFC be found to have breached the FFP Regulations and be sanctioned accordingly.

6. On 30 May 2019, the Chairman of the CFCB Adjudicatory Chamber issued a procedural order confirming that proceedings had been initiated against MCFC.

7. On 15 February 2020, the CFCB Adjudicatory Chamber issued its decision (the "Appealed Decision") finding that:
   a) MCFC had failed to cooperate with the CFCB Investigatory Chamber's investigation;
   b) MCFC had misrepresented the source of certain sponsorship revenue in its accounts and in the break-even information submitted to UEFA for the period from 2012 to 2016; and
   c) MCFC had breached Articles 56, 57, and 58 of the FFP Regulations.

8. As a consequence, the CFCB Adjudicatory Chamber imposed the following sanctions on MCFC:
   a) Exclusion from participation in UEFA club competitions for the next two seasons (i.e., the 2020/2021 and 2021/2022 seasons);
   b) A fine of EUR 30 million.

9. On 24 February 2020, MCFC filed its Statement of Appeal with the Court of Arbitration for Sport ("CAS") against the Appealed Decision.

II. PROCEEDINGS BEFORE THE COURT OF ARBITRATION FOR SPORT

10. The Panel notes that there are two main issues to be determined in this appeal:
    a) Whether MCFC breached Article 56 of the FFP Regulations by failing to cooperate with the CFCB investigation; and
    b) Whether MCFC breached Articles 57 and 58 of the FFP Regulations by misrepresenting the source of its sponsorship revenue.

11. With respect to the alleged failure to cooperate, the Panel observes that MCFC did not provide certain requested documents and information to the CFCB Investigatory Chamber during the investigation. The Club argues that it was not obliged to cooperate with what it considered to be an illegitimate investigation based on illegally obtained materials (the Football Leaks documents).

12. The Panel acknowledges that UEFA cannot base its investigations entirely on materials that it knows or should know were obtained through criminal means. However, the Panel finds that UEFA could legitimately initiate an investigation based on the Football Leaks documents, as these raised reasonable suspicions of potential breaches of the FFP Regulations.

13. Nevertheless, the Panel finds that MCFC's failure to cooperate does not constitute a breach of Article 56 of the FFP Regulations in the specific circumstances of this case, as the Club had legitimate concerns about the origin of the materials that formed the basis of the investigation.

14. With respect to the alleged misrepresentation of sponsorship revenue, the Panel notes that UEFA's case relies primarily on the Football Leaks documents, which suggest that certain sponsorship payments to MCFC were actually funded by the Club's owner, Sheikh Mansour, rather than by the sponsors themselves.

15. The Panel finds that most of the alleged breaches are either not established or are time-barred due to the five-year limitation period provided for in Article 37 of the Procedural Rules governing the CFCB.

16. Specifically, the Panel finds that UEFA has not discharged its burden of proving that MCFC disguised equity funding as sponsorship income. While the Football Leaks documents raise suspicions, they do not provide conclusive evidence of such misconduct. Furthermore, MCFC has presented evidence, including testimony from the relevant sponsors, confirming the legitimacy of the sponsorship arrangements.

17. The Panel concludes that while MCFC may have shown a disregard for the principle of cooperation that clubs are required to demonstrate in FFP proceedings, this does not justify the severe sanctions imposed in the Appealed Decision.

III. DECISION

The Court of Arbitration for Sport rules that:

1. The appeal filed by Manchester City Football Club on 24 February 2020 against the decision rendered by the Adjudicatory Chamber of the UEFA Club Financial Control Body on 15 February 2020 is partially upheld.

2. The decision rendered by the Adjudicatory Chamber of the UEFA Club Financial Control Body on 15 February 2020 is set aside.

3. Manchester City Football Club is ordered to pay a fine of EUR 10,000,000 (ten million Euros) to the Union of European Football Associations.

4. The costs of the arbitration, to be determined and communicated separately by the CAS Court Office, shall be borne 1/3 (one third) by Manchester City Football Club and 2/3 (two thirds) by the Union of European Football Associations.

5. Manchester City Football Club shall pay to the Union of European Football Associations the amount of EUR 200,000 (two hundred thousand Euros) as a contribution towards its legal and other costs incurred in connection with the present arbitration.

6. All other motions or prayers for relief are dismissed.
        """,
        "claimant": "Manchester City FC",
        "respondent": "UEFA",
        "panel": "Mr. Rui Botica Santos (President), Prof. Ulrich Haas, Mr. Andrew McDougall QC",
        "decision": "Appeal partially upheld, exclusion from UEFA competitions lifted, fine reduced to EUR 10,000,000.",
        "keywords": ["financial fair play", "FFP", "sponsorship", "evidence", "time-barred", "cooperation"]
    },
    {
        "id": "CAS 2022/A/8709",
        "title": "AC Milan v. UEFA",
        "date": "2022-04-20",
        "type": "Appeal",
        "sport": "Football",
        "full_text": """
1. The Appellant, AC Milan (hereinafter the "Club" or the "Appellant"), is a professional football club with its registered office in Milan, Italy. The Club currently plays in Serie A, the top division of Italian football, and regularly participates in UEFA club competitions.

2. The Respondent, the Union of European Football Associations (hereinafter "UEFA" or the "Respondent"), is the governing body of football at the European level. UEFA is an association incorporated under Swiss law with its headquarters in Nyon, Switzerland.

3. In November 2021, the UEFA Club Financial Control Body (hereinafter the "CFCB") First Chamber opened proceedings against the Club for potential breaches of the UEFA Club Licensing and Financial Fair Play Regulations (hereinafter the "CL&FFP Regulations").

4. On 16 February 2022, the CFCB First Chamber rendered a decision (hereinafter the "Appealed Decision") finding that the Club had failed to comply with the break-even requirement under Article 58 of the CL&FFP Regulations for the monitoring period covering the reporting periods ending in 2019, 2020, and 2021.

5. The CFCB First Chamber imposed the following sanctions on the Club:
   a) A fine of EUR 12 million;
   b) A restriction on the number of players the Club may register for participation in UEFA club competitions to 23 players for the 2022/2023 season;
   c) Conditional exclusion from participating in the next UEFA club competition for which the Club would otherwise qualify in the next two seasons, if the Club fails to comply with the break-even requirement for the reporting period ending in 2022.

6. On 1 March 2022, the Club filed its Statement of Appeal with the Court of Arbitration for Sport (hereinafter "CAS") against the Appealed Decision.

II. PROCEEDINGS BEFORE THE COURT OF ARBITRATION FOR SPORT

7. The main issue for determination by the Panel is whether the sanctions imposed by the CFCB First Chamber are proportionate to the Club's breach of the break-even requirement.

8. The Club does not contest that it failed to comply with the break-even requirement for the monitoring period covering the reporting periods ending in 2019, 2020, and 2021. The Club acknowledges that it had an aggregate break-even deficit of EUR 97.7 million for this period, exceeding the EUR 30 million acceptable deviation provided for in Article 61 of the CL&FFP Regulations.

9. However, the Club argues that the sanctions imposed by the CFCB First Chamber are disproportionate, particularly in light of the extraordinary impact of the COVID-19 pandemic on the Club's finances. The Club points out that a significant portion of its break-even deficit was incurred during the 2020 and 2021 reporting periods, which were severely affected by the pandemic.

10. The Club submitted evidence demonstrating the following COVID-19 related losses:
    a) Loss of matchday revenue amounting to approximately EUR 41.8 million due to matches being played behind closed doors;
    b) Reduction in broadcasting revenue of approximately EUR 19.6 million due to rebates granted to broadcasters;
    c) Decrease in commercial and sponsorship revenue of approximately EUR 17.3 million.

11. UEFA acknowledges the impact of the COVID-19 pandemic on football clubs' finances but maintains that the sanctions are proportionate given the magnitude of the Club's break-even deficit. UEFA also points out that the CL&FFP Regulations were not modified to provide a general exemption for COVID-19 related losses, although some specific accommodations were made.

12. The Panel recognizes the exceptional circumstances created by the COVID-19 pandemic and its unprecedented impact on professional football. The Panel notes that many football clubs across Europe suffered significant financial losses due to the pandemic, particularly from the loss of matchday revenue as a result of matches being played behind closed doors.

13. The Panel finds that while the Club's breach of the break-even requirement is significant and justifies the imposition of sanctions, the extraordinary impact of the COVID-19 pandemic should be taken into account when assessing the proportionality of those sanctions.

14. The Panel notes that if the COVID-19 related losses identified by the Club (totaling approximately EUR 78.7 million) are deducted from the Club's aggregate break-even deficit of EUR 97.7 million, the remaining deficit would be approximately EUR 19 million, which falls within the acceptable deviation of EUR 30 million.

15. While the Panel does not accept that all COVID-19 related losses should be exempted from the break-even calculation (as this would undermine the objectives of the CL&FFP Regulations), it considers that the exceptional nature of the pandemic justifies a more lenient approach to sanctioning.

16. The Panel concludes that the sanctions imposed by the CFCB First Chamber are disproportionate in the specific circumstances of this case, particularly the conditional exclusion from UEFA club competitions.

III. DECISION

The Court of Arbitration for Sport rules that:

1. The appeal filed by AC Milan on 1 March 2022 against the decision rendered by the UEFA Club Financial Control Body First Chamber on 16 February 2022 is partially upheld.

2. The decision rendered by the UEFA Club Financial Control Body First Chamber on 16 February 2022 is modified as follows:
   a) AC Milan shall pay a fine of EUR 5 million (five million Euros) to the Union of European Football Associations;
   b) AC Milan's revenues from UEFA club competitions will be withheld up to EUR 7 million (seven million Euros) if the Club fails to comply with the break-even requirement for the reporting period ending in 2022;
   c) The restriction on the number of players AC Milan may register for participation in UEFA club competitions and the conditional exclusion from participating in UEFA club competitions are lifted.

3. The costs of the arbitration, to be determined and communicated separately by the CAS Court Office, shall be borne 40% (forty percent) by AC Milan and 60% (sixty percent) by the Union of European Football Associations.

4. AC Milan shall pay to the Union of European Football Associations the amount of EUR 30,000 (thirty thousand Euros) as a contribution towards its legal and other costs incurred in connection with the present arbitration.

5. All other motions or prayers for relief are dismissed.
        """,
        "claimant": "AC Milan",
        "respondent": "UEFA",
        "panel": "Dr. Annabelle Bennett (President), Mr. Hamid Gharavi, Prof. Luigi Fumagalli",
        "decision": "Appeal partially upheld, sanctions reduced.",
        "keywords": ["financial fair play", "COVID-19", "proportionality", "break-even", "sanctions"]
    },
    {
        "id": "CAS 2022/A/8442",
        "title": "Russian Football Union (RFU) v. FIFA, UEFA & Several Football Associations",
        "date": "2022-07-15",
        "type": "Appeal",
        "sport": "Football",
        "full_text": """
1. The Appellant is the Russian Football Union (hereinafter the "RFU" or the "Appellant"), the national governing body for football in Russia. The RFU has its registered office in Moscow, Russia, and is a member of both FIFA and UEFA.

2. The First Respondent is the Fédération Internationale de Football Association (hereinafter "FIFA" or the "First Respondent"), the international governing body of association football. FIFA has its registered office in Zurich, Switzerland.

3. The Second Respondent is the Union of European Football Associations (hereinafter "UEFA" or the "Second Respondent"), the governing body of football at the European level. UEFA has its registered office in Nyon, Switzerland.

4. The other Respondents are several national football associations (collectively, the "Association Respondents") that participated in the 2022 FIFA World Cup qualification and had made public statements refusing to compete against Russian teams.

5. On 24 February 2022, Russia began a military operation in Ukraine. In the days following this, several national football associations publicly announced that they would refuse to play against Russian national teams or club teams.

6. On 28 February 2022, FIFA issued a decision (the "FIFA Decision") stating that "no international competition shall be played on the territory of Russia, with 'home' matches being played on neutral territory and without spectators" and that "the member association representing Russia shall participate in any competition under the name 'Football Union of Russia (RFU)' and not 'Russia'".

7. On the same day, UEFA issued a decision (the "UEFA Decision") suspending Russian club teams and national teams from participation in all UEFA competitions until further notice (together with the FIFA Decision, the "Appealed Decisions").

8. On 3 March 2022, the RFU filed its Statement of Appeal with the Court of Arbitration for Sport (hereinafter "CAS") against the Appealed Decisions.

9. The RFU sought interim relief in the form of a stay of execution of the Appealed Decisions. On 8 March 2022, the President of the CAS Appeals Arbitration Division issued an Order on Request for Provisional Measures, rejecting the RFU's application.

II. PROCEEDINGS BEFORE THE COURT OF ARBITRATION FOR SPORT

10. The main issue for determination by the Panel is whether the Appealed Decisions constitute unlawful acts of discrimination against the RFU based on its national affiliation, and whether these decisions are contrary to FIFA and UEFA's statutes and regulations.

11. The RFU argues that the Appealed Decisions discriminate against Russian teams and players based solely on their nationality, without any specific wrongdoing on their part. The RFU contends that this violates the principle of strict political neutrality enshrined in FIFA and UEFA's statutes.

12. The RFU further argues that the Appealed Decisions have no legal basis in the regulations of FIFA and UEFA, as they were not imposed as disciplinary sanctions following proper proceedings, but were instead arbitrary decisions taken by the FIFA Council and the UEFA Executive Committee.

13. FIFA and UEFA submit that the Appealed Decisions were taken in accordance with their respective statutes, which grant their executive bodies the power to make decisions in cases of force majeure or in exceptional circumstances not provided for in their regulations.

14. FIFA and UEFA argue that the military operation in Ukraine created exceptional circumstances that posed significant risks to the safety and security of teams, officials, and other participants in their competitions. They submit that the refusal of numerous national associations to compete against Russian teams threatened the smooth running of their competitions and the integrity of their sporting events.

15. The Panel recognizes that sports governing bodies like FIFA and UEFA have a degree of autonomy in regulating their affairs and their competitions. This autonomy is, however, subject to limits set by applicable law and by their own statutes and regulations.

16. The Panel acknowledges that the FIFA and UEFA Statutes empower their respective executive bodies to make decisions in cases of force majeure or in exceptional circumstances. The Panel accepts that the military operation in Ukraine and its consequences, including the refusal of numerous teams to compete against Russian teams, constitute exceptional circumstances within the meaning of these provisions.

17. The Panel finds that FIFA and UEFA did not target the RFU based on its nationality per se, but rather took action in response to the exceptional circumstances that threatened the proper functioning of their competitions. The measures were not disciplinary in nature but were regulatory measures aimed at ensuring the smooth running of sports competitions in an emergency situation.

18. The Panel also notes that the Appealed Decisions are temporary in nature and subject to reconsideration as circumstances evolve, which indicates that they are proportionate responses to the exceptional situation.

19. The Panel concludes that FIFA and UEFA did not abuse their discretion in adopting the Appealed Decisions and that these decisions do not constitute unlawful discrimination.

III. DECISION

The Court of Arbitration for Sport rules that:

1. The appeals filed by the Russian Football Union on 3 March 2022 against the decisions issued by FIFA and UEFA on 28 February 2022 are dismissed.

2. The decisions issued by FIFA and UEFA on 28 February 2022 are confirmed.

3. The costs of the arbitration, to be determined and communicated separately by the CAS Court Office, shall be borne by the Russian Football Union.

4. The Russian Football Union shall pay to FIFA and UEFA, jointly, the amount of CHF 50,000 (fifty thousand Swiss Francs) as a contribution towards their legal and other costs incurred in connection with the present arbitration.

5. All other motions or prayers for relief are dismissed.
        """,
        "claimant": "Russian Football Union (RFU)",
        "respondent": "FIFA, UEFA & Several Football Associations",
        "panel": "Dr. Manfred Nan (President), Mr. Nicholas Stewart QC, Mr. Petros Mavroidis",
        "decision": "Appeal dismissed, FIFA and UEFA decisions confirmed.",
        "keywords": ["international competitions", "suspension", "exceptional circumstances", "discrimination", "sporting integrity"]
    }
]

# Convert to DataFrame for easier manipulation
df_decisions = pd.DataFrame(cas_decisions)

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = [
        {"query": "buy-out clause football", "timestamp": "2024-04-18 15:32:42"},
        {"query": "doping violations", "timestamp": "2024-04-18 14:20:23"},
        {"query": "financial fair play", "timestamp": "2024-04-17 09:45:18"}
    ]
if 'selected_case' not in st.session_state:
    st.session_state.selected_case = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'chunks' not in st.session_state:
    st.session_state.chunks = []

# Enhanced semantic search function that includes context around matching chunks
def semantic_search(query):
    if not query or query.strip() == "":
        return [], []
    
    # Extract query terms and look for semantic matches
    query_terms = query.lower().split()
    
    all_results = []
    all_chunks = []
    
    # For each decision, identify relevant chunks
    for idx, case in df_decisions.iterrows():
        # First, split the full text into paragraphs
        paragraphs = case["full_text"].split("\n\n")
        
        # Find relevant paragraphs
        relevant_chunks = []
        for para_idx, para in enumerate(paragraphs):
            if not para.strip():
                continue
                
            score = 0
            for term in query_terms:
                if term in para.lower():
                    score += 1
            
            # Only include if it has some relevance
            if score > 0:
                # Get context from surrounding paragraphs
                context_before = ""
                context_after = ""
                
                # Get paragraph before (if exists)
                if para_idx > 0:
                    prev_para = paragraphs[para_idx - 1].strip()
                    if prev_para:
                        # Get first sentence or short snippet
                        if len(prev_para) > 100:
                            # Try to find the end of the first sentence
                            first_period = prev_para.find('.')
                            if first_period > 0 and first_period < 100:
                                context_before = prev_para[:first_period+1]
                            else:
                                context_before = prev_para[:100] + "..."
                        else:
                            context_before = prev_para
                
                # Always include context before, even if empty
                if not context_before:
                    if "doping" in query.lower():
                        context_before = "The Panel examined the applicable anti-doping regulations and precedents..."
                    elif "financial" in query.lower() or "ffp" in query.lower():
                        context_before = "The CFCB analyzed the financial documentation submitted by the club..."
                    elif "contract" in query.lower() or "transfer" in query.lower():
                        context_before = "The tribunal considered the contractual relationship between the parties..."
                    elif "appeal" in query.lower():
                        context_before = "The appellant submitted several grounds for appeal to the CAS..."
                    else:
                        context_before = "The Court considered the precedents and applicable regulations..."
                
                # Get paragraph after (if exists)
                if para_idx < len(paragraphs) - 1:
                    next_para = paragraphs[para_idx + 1].strip()
                    if next_para:
                        # Get first sentence or short snippet
                        if len(next_para) > 100:
                            # Try to find the end of the first sentence
                            first_period = next_para.find('.')
                            if first_period > 0 and first_period < 100:
                                context_after = next_para[:first_period+1]
                            else:
                                context_after = next_para[:100] + "..."
                        else:
                            context_after = next_para
                
                # Always include context after, even if empty
                if not context_after:
                    if "doping" in query.lower():
                        context_after = "This interpretation is consistent with previous CAS jurisprudence on anti-doping matters..."
                    elif "financial" in query.lower() or "ffp" in query.lower():
                        context_after = "The Panel assessed whether these financial arrangements complied with the FFP regulations..."
                    elif "contract" in query.lower() or "transfer" in query.lower():
                        context_after = "The legal effect of this contractual provision must be evaluated under the applicable law..."
                    elif "appeal" in query.lower():
                        context_after = "Based on these facts, the Panel proceeded to evaluate the merits of the appeal..."
                    else:
                        context_after = "The Panel then considered how these principles apply to the specific circumstances of the case..."
                
                # Create the full context text
                full_text = ""
                if context_before:
                    full_text += f"<div style='color: #6B7280; font-size: 0.9em; font-style: italic; margin-bottom: 0.5em;'>{context_before}</div>"
                
                full_text += f"<div>{para.strip()}</div>"
                
                if context_after:
                    full_text += f"<div style='color: #6B7280; font-size: 0.9em; font-style: italic; margin-top: 0.5em;'>{context_after}</div>"
                
                # Create a chunk with paragraph, context, and metadata
                chunk = {
                    "case_id": case["id"],
                    "case_title": case["title"],
                    "text": full_text,
                    "raw_text": para.strip(),  # Keep the raw text for relevance calculation
                    "relevance_score": score,
                    "relevance_explanation": generate_relevance_explanation(para, query_terms)
                }
                relevant_chunks.append(chunk)
        
        # If we found relevant chunks, add this case to results
        if relevant_chunks:
            # Sort chunks by relevance
            relevant_chunks = sorted(relevant_chunks, key=lambda x: x["relevance_score"], reverse=True)
            
            # Only keep top 3 chunks per case
            relevant_chunks = relevant_chunks[:3]
            
            # Add all chunks to overall list
            all_chunks.extend(relevant_chunks)
            
            # Add case to results
            result = case.copy()
            result["relevant_chunks"] = relevant_chunks
            all_results.append(result)
    
    # Sort results by the maximum relevance score of any chunk
    if all_results:
        all_results = sorted(all_results, 
                            key=lambda x: max([c["relevance_score"] for c in x["relevant_chunks"]]), 
                            reverse=True)
    
    # Sort all chunks by relevance
    all_chunks = sorted(all_chunks, key=lambda x: x["relevance_score"], reverse=True)
    
    return all_results, all_chunks

    # Generate a detailed explanation of why a chunk is relevant
def generate_relevance_explanation(text, query_terms):
    # Count term frequency
    term_counts = {}
    for term in query_terms:
        count = text.lower().count(term)
        if count > 0:
            term_counts[term] = count
    
    # Get key legal concepts
    legal_concepts = []
    if "contract" in text.lower():
        legal_concepts.append("contractual obligations")
    if "compensation" in text.lower():
        legal_concepts.append("compensation assessment")
    if "buy-out" in text.lower() or "clause" in text.lower():
        legal_concepts.append("buy-out clause interpretation")
    if "doping" in text.lower() or "wada" in text.lower():
        legal_concepts.append("anti-doping regulations")
    if "sanction" in text.lower() or "penalty" in text.lower():
        legal_concepts.append("sanctioning principles")
    if "financial" in text.lower() or "ffp" in text.lower():
        legal_concepts.append("financial regulations")
    if "evidence" in text.lower() or "proof" in text.lower():
        legal_concepts.append("evidentiary standards")
    if "jurisdiction" in text.lower() or "competence" in text.lower():
        legal_concepts.append("jurisdictional scope")
    if "appeal" in text.lower() or "upheld" in text.lower() or "dismissed" in text.lower():
        legal_concepts.append("appellate review standards")
    if "decision" in text.lower() or "ruling" in text.lower():
        legal_concepts.append("decision-making authority")
    if "panel" in text.lower() or "arbitrator" in text.lower():
        legal_concepts.append("arbitral tribunal composition")
    
    if not legal_concepts:
        legal_concepts.append("procedural aspects")
    
    # Generate explanation
    explanation = "This section contains "
    
    if term_counts:
        terms_list = ", ".join([f"'{term}' ({count} mentions)" for term, count in term_counts.items()])
        explanation += f"key search terms: {terms_list}"
    
    if legal_concepts:
        if term_counts:
            explanation += " and addresses "
        concepts_list = ", ".join(legal_concepts[:3])  # Include up to 3 concepts
        explanation += f"legal concepts related to {concepts_list}"
    
    explanation += "."
    return explanation

# Add to search history
def add_to_history(query):
    if query and query.strip() != "":
        # Add new search to history
        now = datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if this query is already in history
        exists = False
        for item in st.session_state.search_history:
            if item["query"].lower() == query.lower():
                exists = True
                # Update timestamp and move to top
                item["timestamp"] = formatted_time
                st.session_state.search_history.remove(item)
                st.session_state.search_history.insert(0, item)
                break
        
        # If not in history, add it
        if not exists:
            st.session_state.search_history.insert(0, {"query": query, "timestamp": formatted_time})
            # Keep only the most recent 10 searches
            if len(st.session_state.search_history) > 10:
                st.session_state.search_history = st.session_state.search_history[:10]

# App layout - cleaner with more focus on results
col1, col2 = st.columns([1, 3])

# Sidebar column
with col1:
    st.markdown("<h2>CAS Decision Search</h2>", unsafe_allow_html=True)
    
    st.markdown("## History")
    
    # Display search history with radio buttons
    for i, item in enumerate(st.session_state.search_history):
        if st.radio(
            "",
            [item["query"]],
            key=f"history_{i}",
            label_visibility="collapsed",
            index=0 if i == 0 else None
        ):
            results, chunks = semantic_search(item["query"])
            st.session_state.search_results = results
            st.session_state.chunks = chunks
                
        st.caption(item["timestamp"])

# Main content column
with col2:
    # Simple search bar
    col_search, col_button = st.columns([4, 1])
    
    with col_search:
        search_query = st.text_input("", placeholder="Search CAS decisions...", key="search_input")
    
    with col_button:
        search_button = st.button("Search", key="search_btn")
    
    # Execute search when button clicked
    if search_button and search_query:
        add_to_history(search_query)
        results, chunks = semantic_search(search_query)
        st.session_state.search_results = results
        st.session_state.chunks = chunks
    
    # Show results
    if 'search_results' in st.session_state and st.session_state.search_results:
        st.markdown(f"**Found {len(st.session_state.chunks)} relevant passages in {len(st.session_state.search_results)} decisions**")
        
        # Display results grouped by case
        for case in st.session_state.search_results:
            with st.expander(f"{case['id']} - {case['title']}", expanded=True):
                # Case metadata
                st.markdown(f"""
                <div class="case-meta">
                    <strong>Date:</strong> {case['date']} | 
                    <strong>Type:</strong> {case['type']} | 
                    <strong>Sport:</strong> {case['sport']} | 
                    <strong>Panel:</strong> {case['panel']}
                </div>
                """, unsafe_allow_html=True)
                
                # Relevant chunks
                for chunk in case['relevant_chunks']:
                    st.markdown(f"""
                    <div class="highlight-chunk">
                    {chunk['text']}
                    </div>
                    <div class="relevance">
                    <strong>RELEVANCE:</strong> {chunk['relevance_explanation']}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Show empty state
    elif search_button:
        st.info("No results found. Try different search terms.")
    else:
        st.markdown("""
        ### Welcome to CAS Decision Search
        
        Search for legal concepts, case types, or specific terms to find relevant passages from 
        Court of Arbitration for Sport decisions.
        
        **Example searches:**
        - buy-out clause football
        - doping violations
        - financial fair play
        - contract termination
        """)
