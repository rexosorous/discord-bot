import utilities as util



def get_clipv2Test():
    print( "Running get_clipv2Test..." )
    clipBank = {"i'm fucking gay",
                "no, what the fuck",
                "damn girl, is your titty a penis because i wanna suck on it",
                "bone apple tit",
                "what the fuck did you say to me",
                "you stole all my glory",
                "you're a man, holy shit"}
    searchTermA = {"fucking","gay"}
    searchTermB = {"bone","tit"}
    searchTermC = {"you","all"}
    searchTermD = ('tit', 'penis')
    if( ( util.get_clipv2( clipBank, searchTermA ) != "i'm fucking gay" ) or
        ( util.get_clipv2( clipBank, searchTermB ) != "bone apple tit" ) or
        ( util.get_clipv2( clipBank, searchTermC ) != "you stole all my glory") or
        ( util.get_clipv2( clipBank, searchTermD ) != "damn girl, is your titty a penis because i wanna suck on it") ):
        raise Exception("get_clipv2Test Failed")
    print( "Test passed!" )



def get_clipv3Test():
    print('Running get_clipv3Test...')
    searchTermA = 'fucking gay'
    searchTermB = 'bone tit'
    searchTermC = 'you all'
    searchTermD = 'tit penis'
    if( (util.get_clipv3(searchTermA) != "i'm fucking gay.mp3") or
        (util.get_clipv3(searchTermB) != "bone apple tit.mp3") or
        (util.get_clipv3(searchTermC) != "you stole all my glory.mp3") or
        (util.get_clipv3(searchTermD) != "damn girl, is your titty a penis because i wanna suck on it.mp3") ):
        raise Exception("get_clipv3Test Failed")
    print('Test passed!')



def runTests():
    # get_clipv2Test()
    get_clipv3Test()



runTests()