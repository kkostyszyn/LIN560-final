
import pynini
import functools 

A = functools.partial(pynini.acceptor, token_type="utf8")
T = functools.partial(pynini.transducer, input_token_type="utf8", output_token_type="utf8")

#define phonemic inventory
#for the most part, I'm using the orthography as a guide rather than
#strictly adhering to IPA - thus, 'y' is used in place of IPA 'j'. however,
#for certain phones that are represented with multiple characters in
#orthography, i vary between using a multicharacter symbol (as in [ts])
#or the IPA symbol (as in ʃ), depending on the length of the IPA
#equivalent.

vowels = (A("a") | A("e") | A("i") | A("o") | A("u"))

consonant = (A("b") | A("c") | A("d") | A("f") |  A("g") | A("h") | A("k") | A("m") | A("n") | A("r") | A("s") | A("ʃ") | A("t") | A("C") | A("w") | A("y") | A("z") | A("[ts]") | A("[ch]"))

#in general, words with -iru or -eru belong to group 2, but some verbs
#such as 'hairu' belong to group 1. these exceptions will be given the
#[g1] tag as a sort of lexical marker so the root is extracted properly.
marker = (A("1") | A("2") | A("[kuru]") | A("[suru]") | A(" ")) 

sigmaStar = pynini.closure(vowels | consonant | marker)

#define lexicon
#not a complete lexicon, but will simplify test cases

tokens1 = [A("kuru"), 
    A("suru"), 
    A("aru"), 
    A("dasu"), 
    A("isogu"), 
    A("iu"), 
    A("hairu1"), 
    A("shiru1"), 
    A("ageru"), 
    A("dekiru"), 
    A("iru"),
    A("iru1"),
    A("kangaeru"),
    A("miru"),
    A("taberu")]
    
tokens2 = [A("kaku"),
    A("kakureru"),
    A("kawaku"),
    A("kau"),
    A("matsu"),
    A("tatsu"),
    A("nuru"),
    A("omou"),
    A("shinu"),
    A("tobu"),
    A("toru"),
    A("yomu")]
    
tokens3 = [A("akirameru"),
    A("arau"),
    A("aruku"),
    A("atsumaru"),
    A("atsumeru"),
    A("au"),
    A("chigau"),
    A("fueru"),
    A("erabu"),
    A("gozaru"),
    A("maniau"),
    A("you"),
    A("yobu"),
    A("yaku")]


#######MORPHOLOGICAL PROCESSES######

#extract root - fix some symbols
shi_IPA = pynini.cdrewrite(T("sh", "ʃ"), sigmaStar, sigmaStar, sigmaStar)
ts_IPA = pynini.cdrewrite(T("ts", "[ts]"), sigmaStar, sigmaStar, sigmaStar)
ch_IPA = pynini.cdrewrite(T("ch", "[ch]"), sigmaStar, sigmaStar, sigmaStar)

kuru = pynini.cdrewrite(T("kuru", "[kuru]"), "[BOS]", "[EOS]", sigmaStar)
suru = pynini.cdrewrite(T("suru", "[suru]"), "[BOS]", "[EOS]", sigmaStar)

ru_root = (T("eru", "e2") | T("iru" , "i2")).optimize()
ru_drop = pynini.cdrewrite(ru_root, sigmaStar, "[EOS]", sigmaStar)

u_root = (T("u1", "1") | T("u", "1")).optimize()
u_drop = pynini.cdrewrite(u_root, sigmaStar, "[EOS]", sigmaStar) 

root = (shi_IPA @ ts_IPA @ ch_IPA @ kuru @ suru @ ru_drop @ u_drop).optimize()

#PLAIN
#affirmative present - returns the form itself

kuru_plain_ap = pynini.cdrewrite(T("[kuru]", "kuru"), "[BOS]", "[EOS]", sigmaStar)
suru_plain_ap = pynini.cdrewrite(T("[suru]", "suru"), "[BOS]", "[EOS]", sigmaStar)
ru_plain_ap_changes = (T("e2", "eru") | T("i2" , "iru")).optimize()
ru_plain_ap = pynini.cdrewrite(ru_plain_ap_changes, sigmaStar, "[EOS]", sigmaStar)
u_plain_ap_changes = (T("1", "u")).optimize()
u_plain_ap = pynini.cdrewrite(u_plain_ap_changes, sigmaStar, "[EOS]", sigmaStar)
plain_affirmative_present = (kuru_plain_ap @ suru_plain_ap @ ru_plain_ap @ u_plain_ap).optimize()

#affirmative past
#NEEDS WORK to handle more exceptions in group 1
kuru_plain_apa = pynini.cdrewrite(T("[kuru]", "kita"), "[BOS]", "[EOS]", sigmaStar)
suru_plain_apa = pynini.cdrewrite(T("[suru]", "ʃita"), "[BOS]", "[EOS]", sigmaStar)
ru_plain_apa_changes = (T("2","ta"))
ru_plain_apa = pynini.cdrewrite(ru_plain_apa_changes, sigmaStar, "[EOS]", sigmaStar)
#'isogu'
u_plain_apa_isogu = pynini.cdrewrite(T("g1", "ida"), "iso", "[EOS]", sigmaStar)
u_plain_apa_changes = (T("1","tta"))
u_plain_apa = pynini.cdrewrite(u_plain_apa_changes, sigmaStar, "[EOS]", sigmaStar)
#yomu
#tobu -> tonda
u_plain_apa_nda_changes = (T("mtta", "nda") | T("btta", "nda") | T("ntta", "nda"))
u_plain_apa_nda = pynini.cdrewrite(u_plain_apa_nda_changes, sigmaStar, "[EOS]", sigmaStar)
plain_affirmative_past = (kuru_plain_apa @ suru_plain_apa @ ru_plain_apa @ u_plain_apa_isogu @ u_plain_apa @ u_plain_apa_nda).optimize()

#negative present
kuru_plain_np = pynini.cdrewrite(T("[kuru]", "konai"), "[BOS]", "[EOS]", sigmaStar)
suru_plain_np = pynini.cdrewrite(T("[suru]", "ʃinai"), "[BOS]", "[EOS]", sigmaStar)
ru_plain_np_changes = (T("2","nai"))
ru_plain_np = pynini.cdrewrite(ru_plain_np_changes, sigmaStar, "[EOS]", sigmaStar)
#'aru' vowel deletion
u_plain_np_aru = pynini.cdrewrite(T("ar1", "nai"), "[BOS]", "[EOS]", sigmaStar) 
#'w' insertation
u_plain_np_vowel_changes = (T("1", "wanai"))
u_plain_np_vowel = pynini.cdrewrite(u_plain_np_vowel_changes, vowels, "[EOS]", sigmaStar)
u_plain_np_changes = (T("1","anai"))
u_plain_np = pynini.cdrewrite(u_plain_np_changes, sigmaStar, "[EOS]", sigmaStar)
plain_negative_present = (kuru_plain_np @ suru_plain_np @ ru_plain_np @ u_plain_np_aru @ u_plain_np_vowel @ u_plain_np).optimize()

#negative past 

plain_npa = (plain_negative_present + T("", "katta")).optimize()
plain_npa_fix = pynini.cdrewrite(T("i", ""), "na", "katta[EOS]", sigmaStar).optimize()
plain_negative_past = (plain_npa @ plain_npa_fix).optimize()

#POLITE
#affirmative present
kuru_polite_ap = pynini.cdrewrite(T("[kuru]", "kimasu"), "[BOS]", "[EOS]", sigmaStar)
suru_polite_ap = pynini.cdrewrite(T("[suru]", "ʃimasu"), "[BOS]", "[EOS]", sigmaStar)
ru_polite_ap_changes = (T("2","masu"))
ru_polite_ap = pynini.cdrewrite(ru_polite_ap_changes, sigmaStar, "[EOS]", sigmaStar)
u_polite_ap_changes = (T("1","imasu"))
u_polite_ap = pynini.cdrewrite(u_polite_ap_changes, sigmaStar, "[EOS]", sigmaStar)
gozaimasu = pynini.cdrewrite(T("r", ""), "goza", "imasu[EOS]", sigmaStar)
polite_affirmative_present = (kuru_polite_ap @ suru_polite_ap @ ru_polite_ap @ u_polite_ap @ gozaimasu).optimize()

#affirmative past
#-masu plus -ita
polite_apa = (polite_affirmative_present + T("", "ita")).optimize()
polite_apa_fix = pynini.cdrewrite(T("suita", "ʃita"), "ma", "[EOS]", sigmaStar) 
polite_affirmative_past = (polite_apa @ polite_apa_fix).optimize()


#negative present
#-masu plus -en
polite_np = (polite_affirmative_present + T("", "en")).optimize()
polite_np_fix = pynini.cdrewrite(T("suen", "sen"), "ma", "[EOS]", sigmaStar)
polite_negative_present = (polite_np @ polite_np_fix).optimize()


#negative past
#change T(deshita) to be the actual perfective of desu, when perfective is complete
polite_negative_past = (polite_negative_present + T("", " deʃita")).optimize()

#######TE FORM #######
te_a_env = (A("t") | A("nd"))
te_a= pynini.cdrewrite(T("a", "e"), consonant, "[EOS]", sigmaStar)
#for the form 'yaite', the surface form stayed 'yatte' despite the 
#affirmative for and the underlying 'yaktte', so this one had to be
#manually overwritten 
yaite = pynini.cdrewrite(T("kt", "i"), "[BOS]ya", "te", sigmaStar)
te_affirmative = (plain_affirmative_past @ te_a @ yaite).optimize()

te_n = pynini.cdrewrite(T("atta", "ute"), "nak", "[EOS]", sigmaStar)
te_negative = (plain_negative_past @ te_n).optimize()

#######CONDITIONAL########
#plain affirmative
kuru_cond_pa = pynini.cdrewrite(T("[kuru]", "kureba"), "[BOS]", "[EOS]", sigmaStar)
suru_cond_pa = pynini.cdrewrite(T("[suru]", "sureba"), "[BOS]", "[EOS]", sigmaStar)
ru_cond_pa_changes = (T("2","reba"))
ru_cond_pa = pynini.cdrewrite(ru_cond_pa_changes, sigmaStar, "[EOS]", sigmaStar)
u_cond_pa_changes = (T("1","eba"))
u_cond_pa = pynini.cdrewrite(u_cond_pa_changes, sigmaStar, "[EOS]", sigmaStar)
conditional_plain_affirmative = (kuru_cond_pa @ suru_cond_pa @ ru_cond_pa @ u_cond_pa).optimize()

#plain affirmative 2 
conditional_plain_affirmative_2 = (plain_affirmative_past + T("", " ra")).optimize()

#plain negative
cond_pn = (plain_negative_past + T("", "ereba")).optimize()
cond_pn_fix = pynini.cdrewrite(T("atta", ""), "nak", "ereba", sigmaStar)
conditional_plain_negative = (cond_pn @ cond_pn_fix).optimize()

#plain negative 2
conditional_plain_negative_2 = (plain_negative_past + T("", " ra")).optimize()

#formal affirmative - affirmative past masu + ra
conditional_formal_affirmative = (polite_affirmative_past + T("", " ra")).optimize()

#formal negative - negative past masu + ra
conditional_formal_negative = (polite_negative_past + T("", " ra")).optimize()

#######VOLITIOINAL#######
#plain
kuru_vp = pynini.cdrewrite(T("[kuru]", "koyoo"), "[BOS]", "[EOS]", sigmaStar)
suru_vp = pynini.cdrewrite(T("[suru]", "ʃiyoo"), "[BOS]", "[EOS]", sigmaStar)
ru_vp_changes = (T("2", "yoo"))
ru_vp = pynini.cdrewrite(ru_vp_changes, sigmaStar, "[EOS]", sigmaStar)
u_vp_changes = (T("1", "oo"))
u_vp = pynini.cdrewrite(u_vp_changes, sigmaStar, "[EOS]", sigmaStar)
volitional_plain = (kuru_vp @ suru_vp @ ru_vp @ u_vp).optimize()
#formal
kuru_vf = pynini.cdrewrite(T("[kuru]", "kimashoo"), "[BOS]", "[EOS]", sigmaStar)
suru_vf = pynini.cdrewrite(T("[suru]", "ʃimashoo"), "[BOS]", "[EOS]", sigmaStar)
ru_vf_changes = (T("2", "maʃoo"))
ru_vf = pynini.cdrewrite(ru_vf_changes, sigmaStar, "[EOS]", sigmaStar)
u_vf_changes = (T("1", "imaʃoo"))
u_vf = pynini.cdrewrite(u_vf_changes, sigmaStar, "[EOS]", sigmaStar)
#for gozaimashoo, I originally intended to only delete the 'r', 
#as I had done for the polite form - however, this wasn't changing
#as intended, and I was unable to find the problem, so I changed the
#full volitional form instead
gozaimashoo = pynini.cdrewrite(T("gozarimaʃoo", "gozaimaʃoo"), "[BOS]", "[EOS]", sigmaStar)
volitional_formal = (kuru_vf @ suru_vf @ ru_vf @ u_vf @ gozaimashoo).optimize()

#######IMPERATIVE########
#affirmative
kuru_i = pynini.cdrewrite(T("[kuru]", "koi"), "[BOS]", "[EOS]", sigmaStar)
suru_i = pynini.cdrewrite(T("[suru]", "ʃiro"), "[BOS]", "[EOS]", sigmaStar)
ru_ia_changes = (T("2", "ro"))
ru_ia = pynini.cdrewrite(ru_ia_changes, sigmaStar, "[EOS]", sigmaStar)
u_ia_changes = (T("1", "e"))
u_ia = pynini.cdrewrite(u_ia_changes, sigmaStar, "[EOS]", sigmaStar)
imperative_affirmative = (kuru_i @ suru_i @ ru_ia @ u_ia).optimize() 

#negative
imperative_negative = (plain_affirmative_present + T("", " na")).optimize()

#######PHONOLOGICAL PROCESSES#######

#tsu/chi/else
tsu = pynini.cdrewrite(T("C", "[ts]"), sigmaStar, "u", sigmaStar).optimize()
chi_changes = (T("C", "[ch]") | T("[ts]", "[ch]"))
chi = pynini.cdrewrite(chi_changes, sigmaStar, "i", sigmaStar).optimize()
tV_changes = (T("C", "t") | T("[ts]", "t"))
tV = pynini.cdrewrite(tV_changes, sigmaStar, vowels - "u", sigmaStar).optimize()

#s->ʃi before tt
shitta = pynini.cdrewrite(T("s", "ʃi"), sigmaStar, "tta[EOS]", sigmaStar).optimize()

#k->i before tt
k_raise = pynini.cdrewrite(T("kt", "i"), sigmaStar, "ta[EOS]", sigmaStar).optimize()

#consonant delete before tt
tt = (A("tte[EOS]") | A("tta[EOS]"))
con_delete = pynini.cdrewrite(T(consonant, ""), sigmaStar, tt, sigmaStar).optimize()


#s->ʃ
shi = pynini.cdrewrite(T("s", "ʃ"), sigmaStar, "i", sigmaStar).optimize()

#ts -> ch

#fix symbols 
symbol_changes = (T("[ts]","ts") | T("[ch]", "ch") | T("ʃ", "sh"))
symbols = pynini.cdrewrite(symbol_changes, sigmaStar, sigmaStar, sigmaStar)


phonology = (tsu @ chi @ tV @ shitta @ k_raise @ con_delete @ shi @ symbols).optimize()




def paradigm(word):
    temp = word @ root
    print("root:" + temp.stringify(token_type="utf8") + "\n")
    print(
        "Plain Affirmative Present: \t" + (temp @ plain_affirmative_present @ phonology).stringify(token_type="utf8"), 
        "\nPlain Affirmative Past: \t" + (temp @ plain_affirmative_past @ phonology).stringify(token_type="utf8"), 
        "\nPlain Negative Present: \t" + (temp @ plain_negative_present @ phonology).stringify(token_type="utf8"),
        "\nPlain Negative Past: \t\t" + (temp @ plain_negative_past @ phonology).stringify(token_type="utf8"),
        "\nPolite Affirmative Present: \t" + (temp @ polite_affirmative_present @ phonology).stringify(token_type="utf8"),
        "\nPolite Affirmative Past: \t" + (temp @ polite_affirmative_past @ phonology).stringify(token_type="utf8"),
        "\nPolite Negative Present: \t" + (temp @ polite_negative_present @ phonology).stringify(token_type="utf8"),
        "\nPolite Negative Past: \t\t" + (temp @ polite_negative_past @ phonology).stringify(token_type="utf8"),
        "\n-te Affirmative: \t\t" + (temp @ te_affirmative @ phonology).stringify(token_type="utf8"),
        "\n-te Negative: \t\t\t" + (temp @ te_negative @ phonology).stringify(token_type="utf8"),
        "\nConditional Plain Affirmative: \t" + (temp @ conditional_plain_affirmative @ phonology).stringify(token_type="utf8") + " / " + (temp @ conditional_plain_affirmative_2 @ phonology).stringify(token_type="utf8"), 
        "\nConditional Plain Negative: \t" + (temp @ conditional_plain_negative @ phonology).stringify(token_type="utf8") + " / " + (temp @ conditional_plain_negative_2 @ phonology).stringify(token_type="utf8"), 
        "\nConditional Formal Affirmative: " + (temp @ conditional_formal_affirmative @ phonology).stringify(token_type="utf8"),
        "\nConditional Formal Negative: \t" + (temp @ conditional_formal_negative @ phonology).stringify(token_type="utf8"), 
        "\nVolitional Plain: \t\t" + (temp @ volitional_plain @ phonology).stringify(token_type="utf8"), 
        "\nVolitional Formal: \t\t" + (temp @ volitional_formal @ phonology).stringify(token_type="utf8"),
        "\nImperative Affirmative: \t" + (temp @ imperative_affirmative @ phonology).stringify(token_type="utf8"),
        "\nImperative Negative: \t\t" + (temp @ imperative_negative @ phonology).stringify(token_type="utf8"),
        "\n-----------")
        
def run(tokens):
    for token in tokens:
        paradigm(token)
        
def info():
    #print(info)
    print("FST for Japanese verb conjugation. Use paradigm() for a full listing.   Currently functional for:\n\nplain affirmative present\n" +  
        "\tplain affirmative past\n" + 
        "\tplain negative present\n" +
        "\tplain negative past\n" +
        "\tpolite affirmative present\n" +
        "\tpolite_affirmative_past\n" +
        "\tpolite_negative_present\n" +
        "\tpolite_negative_past\n" +
        "\t-te affirmative\n" + 
        "\t-te negative\n" + 
        "\tconditional_plain_affirmative\n" +
        "\tconditional_plain_negative\n" +
        "\tconditional_formal_affirmative\n" +
        "\tconditional_formal_negative\n\n")
    print("There are three pre-made lists of tokens (tokens1, tokens2, toknns3). To run on these lists, use the run() function with the list of your choosing.\n")
    print("To run on a word of your own choosing, use the paradigm() functionn instead, using the acceptor for your word in standard orthography. (Long vowels should be expressed with doubled vowel symbols rather than the vowel with a bar overhead. If a word is group 1/u-dropping but ends in -eru or -iru, making it ambiguous, please mark the word with a 1 at the end as a lexical marker (as in 'hairu1').)")

info()

###READY-MADE TESTS###
#run(tokens3)


