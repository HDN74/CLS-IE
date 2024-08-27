
import owlready2 as owl
import pandas as pd
onto = owl.get_ontology("http://test.org/onto.owl")
from unidecode import unidecode

def chuyen_doi_khong_dau(text):
    return unidecode(text)


with onto:
    class Word(owl.Thing): 
        pass
    
    class Chu_the(Word):
        pass
    class Chu_the_ban_hanh(Chu_the): 
        pass 
    class Chu_the_tham_quyen(Chu_the):
        pass
    
    class Verb(Word):
        pass
    class Verb_tham_quyen(Verb): 
        pass 
    class Verb_ban_hanh(Verb):
        pass
    class Quyen_han(Verb):
        pass
    
    class has_nmod(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_dob(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_sub(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    class has_agency(owl.ObjectProperty, owl.IrreflexiveProperty): 
        domain = [Word]
        range = [Word]
    
    rule1 = owl.Imp()
    rule1.set_as_rule(
        "has_sub(?v, ?a), has_dob(?v, ?d), Chu_the_ban_hanh(?a), Quyen_han(?d) -> has_agency(?d, ?a)"
    )
    #"has_nmod(?a, ?b), has_nmod(?b, ?c), has_sub(?a, ?v), has_dob(?d, ?v), Chu_the_ban_hanh(?a), Quyen_han(?d) -> has_agency(?a, ?d)"



co = Verb("có")
trach_nhiem = Quyen_han("trách_nhiệm")
uy_ban_nhan_dan = Chu_the_ban_hanh("Ủy_ban_nhân_dân")
# cap = Word("cấp")
# tinh = Word("tỉnh")

# owl.AllDifferent([co, trach_nhiem, uy_ban_nhan_dan, cap, tinh])

co.has_sub.append(uy_ban_nhan_dan)

# uy_ban_nhan_dan.has_nmod.append(cap)

# cap.has_nmod.append(tinh)

co.has_dob.append(trach_nhiem)

instances = list(onto.individuals())
print(instances)
instances_in_class = list(Quyen_han.instances())
print(instances_in_class)
owl.sync_reasoner_hermit(infer_property_values=True)
print(trach_nhiem.has_agency)

    
df = pd.read_excel('/home/huydn74/Documents/legal-information-extraction-main/KQDP.xlsx')


for i in range(len(df)):
    label = df['Label'][i]
    word = df['Word'][i]
    head = df['Head'][i]
    category = df['Category'][i]
    
    if category == 'Khong thuoc dang nao':
        continue
    
    print(word)
    
    #str = f"{chuyen_doi_khong_dau(word)} = {chuyen_doi_khong_dau(category)}({word})"
    #print(str)
for i in range(len(df)):
    label = df['Label'][i]
    word = df['Word'][i]
    head = df['Head'][i]
    str = f"{head}.has_{label}.append({word})"
    #print(str)