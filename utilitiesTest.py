import utilities as util

def get_clipv2Test():
    print( "Running get_clipv2Test..." )
    clipBank = {"i'm fucking gay":"clip1",
                "no, what the fuck":"clip2",
                "damn girl, is your titty a penis because i wanna suck on it":"clip3",
                "bone apple tit":"clip4",
                "what the fuck did you say to me":"clip5",
                "you stole all my glory":"clip6"}
    searchTermA = {"fucking","gay"}
    searchTermB = {"bone","tit"}
    searchTermC = {"you","all"}
    searchTermD = {"tit","penis"}
    if( ( util.get_clipv2( clipBank, searchTermA ) != "i'm fucking gay" ) or
        ( util.get_clipv2( clipBank, searchTermB ) != "bone apple tit" ) or
        ( util.get_clipv2( clipBank, searchTermC ) != "you stole all my glory") or
        ( util.get_clipv2( clipBank, searchTermD ) != "damn girl, is your titty a penis because i wanna suck on it") ):
        raise Exception("get_clipv2Test Failed")
    print( "Test passed!" )

def runTests():
    get_clipv2Test()

runTests()