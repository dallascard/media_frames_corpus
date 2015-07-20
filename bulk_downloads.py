import os
import glob

# get search strings that will correspond to < 500 articles
def get_search_strings(url_base, download_dir, subject):
    
    if subject == 'immigration':
        search_strings = get_immigration_searches(url_base, download_dir)
    elif subject == 'smoking':
        search_strings = get_smoking_searches(url_base, download_dir)        
    elif subject == 'samesex':
        search_strings = get_samesex_searches(url_base, download_dir)        
    else:
        search_strings = []

    print len(search_strings), " search strings"
    return search_strings



def get_immigration_searches(url_base, download_dir):

    searches = {}

    # NYT
    searches[6742] = []
    searches[6742].append('+AND+DATE+BEFORE+January+1+1973')
    searches[6742].append('+AND+DATE+AFTER+January+1+1973+AND+DATE+BEFORE+January+2+1976')
    searches[6742].append('+AND+DATE+AFTER+January+1+1976+AND+DATE+BEFORE+June+2+1980')
    for year in range(1980, 2000):
        searches[6742].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+May+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+May+1+' + str(year) + '+AND+DATE+BEFORE+September+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+September+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2000, 2013):
        searches[6742].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+March+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+March+1+' + str(year) + '+AND+DATE+BEFORE+May+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+May+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+September+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+September+1+' + str(year) + '+AND+DATE+BEFORE+November+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+November+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # PALM BEACH POST (done)
    #if len(files) < 25:        
    searches[144576] = []
    for year in range(1988, 2013):
        searches[144576].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    
    # St. Louis Post Dispatch (done)
    searches[11810] = []
    searches[11810].append('+AND+DATE+AFTER+January+1+1988+AND+DATE+BEFORE+January+2+1990')
    for year in range(1990, 2000):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    searches[11810].append('+AND+DATE+AFTER+January+1+2000+AND+DATE+BEFORE+July+2+2000')
    searches[11810].append('+AND+DATE+AFTER+July+1+2000+AND+DATE+BEFORE+January+2+2001')
    for year in range(2001, 2006):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2008):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[11810].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2008, 2013):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    
    # San Jose mercury news
    searches[313960] = []
    for year in range(1994, 2006):
        searches[313960].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[313960].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2007):
        searches[313960].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+April+2+' + str(year))
        searches[313960].append('+AND+DATE+AFTER+April+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[313960].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+October+2+' + str(year))
        searches[313960].append('+AND+DATE+AFTER+October+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2007, 2013):
        searches[313960].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[313960].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))


    # St. Paul Pioneer Press
    searches[313961] = []
    searches[313961] = []
    searches[313961].append('+AND+DATE+AFTER+January+1+1994+AND+DATE+BEFORE+January+2+1996')
    for year in range(1996, 2006):
        searches[313961].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2007):
        searches[313961].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[313961].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2007, 2013):
        searches[313961].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    

    # Washington post
    searches[8075] = []
    searches[8075].append('+AND+DATE+BEFORE+January+2+1992')
    for year in range(1992, 2001):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2001, 2006):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+April+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+April+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+October+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+October+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2007):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+April+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+April+1+' + str(year) + '+AND+DATE+BEFORE+May+16+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+May+15+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+October+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+October+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2007, 2013):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+April+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+April+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+October+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+October+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # Washington Post blogs
    searches[409005] = []
    for year in range(2012, 2013):
        searches[409005].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # Herald Sun
    searches[278130] = []
    searches[278130].append('+AND+DATE+AFTER+January+1+1994+AND+DATE+BEFORE+January+2+2000')
    for year in range(2000, 2013):
        searches[278130].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    searches[278131] = []
    searches[278131].append('+AND+DATE+AFTER+January+1+1994+AND+DATE+BEFORE+January+2+2013')

    # USA TODAY
    searches[8213] = []
    for year in range(1988, 1989):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+2))
    for year in range(1990, 1997):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2013):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # St. Petersburg Times
    searches[11063] = []
    for year in range(1988, 2006):
        searches[11063].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2007):
        searches[11063].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[11063].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2007, 2013):
        searches[11063].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # Philadelphia Inquirer
    searches[247189] = []
    for year in range(1994, 2006):
        searches[247189].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2007):        
        searches[247189].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[247189].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2007, 2013):
        searches[247189].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # Atlanta Journal and Constitution
    searches[8379] = []
    for year in range(1991, 1999):
        searches[8379].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(1999, 2006):        
        searches[8379].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8379].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2006, 2008):        
        searches[8379].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+April+2+' + str(year))
        searches[8379].append('+AND+DATE+AFTER+April+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8379].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2008, 2013):
        searches[8379].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # NYT Blogs
    searches[379740] = []
    for year in range(2011, 2013):        
        searches[379740].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[379740].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    

    # Daily News
    searches[151550] = []
    for year in range(1995, 2013):
        searches[151550].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[151550].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    

    # Denver Post
    searches[144565] = []
    for year in range(2006, 2007):        
        searches[144565].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[144565].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2007, 2013):
        searches[144565].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))


    search_strings = []
    for csi in searches.keys():
        for date_string in searches[csi]:
            search = url_base + '/hottopics/lnacademic/?verb=sr&csi=' + str(csi) + '&sr=SUBJECT(immigration)+AND+GEOGRAPHIC(UNITED+STATES)' + date_string
            search_strings.append(search)

    return search_strings


def get_smoking_searches(url_base, download_dir):

    searches = {}

    # NYT
    searches[6742] = []
    searches[6742].append('+AND+DATE+BEFORE+January+1+1973')
    searches[6742].append('+AND+DATE+AFTER+January+1+1973+AND+DATE+BEFORE+January+2+1976')
    searches[6742].append('+AND+DATE+AFTER+January+1+1976+AND+DATE+BEFORE+June+2+1980')
    for year in range(1980, 2013):
        searches[6742].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+May+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+May+1+' + str(year) + '+AND+DATE+BEFORE+September+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+September+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # PALM BEACH POST (done)
    #if len(files) < 25:        
    searches[144576] = []
    for year in range(1988, 2013):
        searches[144576].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    
    # St. Louis Post Dispatch (done)
    searches[11810] = []
    searches[11810].append('+AND+DATE+AFTER+January+1+1988+AND+DATE+BEFORE+January+2+1990')
    for year in range(1990, 1998):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(1998, 1999):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[11810].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(1999, 2013):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    
    # San Jose mercury news
    searches[313960] = []
    for year in range(1994, 2013):
        searches[313960].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))


    # St. Paul Pioneer Press
    searches[313961] = []
    searches[313961].append('+AND+DATE+AFTER+January+1+1988+AND+DATE+BEFORE+January+2+1996')
    for year in range(1996, 2013):
        searches[313961].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    

    # Washington post
    searches[8075] = []
    searches[8075].append('+AND+DATE+BEFORE+January+2+1995')
    for year in range(1995, 1998):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))        
    for year in range(1998, 2013):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    

    # Washington Post blogs
    searches[409005] = []
    searches[409005].append('+AND+DATE+BEFORE+January+2+2013')

    # Herald Sun
    searches[278130] = []
    searches[278130].append('+AND+DATE+BEFORE+January+2+1997')
    for year in range(1997, 2013):
        searches[278130].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    searches[278131] = []
    searches[278131].append('+AND+DATE+BEFORE+January+2+2013')

    # USA TODAY
    searches[8213] = []
    for year in range(1988, 1989):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+2))
    for year in range(1990, 1997):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2013):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # St. Petersburg Times
    searches[11063] = []
    for year in range(1988, 2006):
        searches[11063].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2007):
        searches[11063].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[11063].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2007, 2013):
        searches[11063].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # Philadelphia Inquirer
    searches[247189] = []
    for year in range(1994, 2006):
        searches[247189].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2007):        
        searches[247189].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[247189].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2007, 2013):
        searches[247189].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # Atlanta Journal and Constitution
    searches[8379] = []
    for year in range(1991, 2002):
        searches[8379].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2003, 2004):
        searches[8379].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2005, 2013):
        searches[8379].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))


    # NYT Blogs
    searches[379740] = []
    for year in range(2011, 2013):        
        searches[379740].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[379740].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    

    # Daily News
    searches[151550] = []
    for year in range(1995, 2013):
        searches[151550].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[151550].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    

    # Denver Post
    searches[144565] = []
    for year in range(1994, 2013):
        searches[144565].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))


    search_strings = []
    for csi in searches.keys():
        for date_string in searches[csi]:
            search = url_base + '/hottopics/lnacademic/?verb=sr&csi=' + str(csi) + '&sr=SUBJECT(smoking)+AND+GEOGRAPHIC(UNITED+STATES)' + date_string
            search_strings.append(search)

    return search_strings



def get_samesex_searches(url_base, download_dir):

    searches = {}

    # PALM BEACH POST (done)
    searches[144576] = []
    for year in range(1988, 2013):
        searches[144576].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))

    # Denver Post
    searches[144565] = []
    for year in range(1994, 2013):
        searches[144565].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    
    # St. Louis Post Dispatch (done)
    searches[11810] = []
    searches[11810].append('+AND+DATE+AFTER+January+1+1988+AND+DATE+BEFORE+January+2+1989')
    for year in range(1989, 2004):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[11810].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2004, 2006):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+May+2+' + str(year))
        searches[11810].append('+AND+DATE+AFTER+May+1+' + str(year) + '+AND+DATE+BEFORE+September+2+' + str(year))
        searches[11810].append('+AND+DATE+AFTER+September+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2013):
        searches[11810].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[11810].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))


    # San Jose mercury news
    searches[313960] = []
    for year in range(1994, 2004):
        searches[313960].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2004, 2013):
        searches[313960].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[313960].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))


    
    # St. Paul Pioneer Press
    searches[313961] = []
    searches[313961].append('+AND+DATE+AFTER+January+1+1988+AND+DATE+BEFORE+January+2+1996')
    for year in range(1996, 2004):
        searches[313961].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2004, 2013):
        searches[313961].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[313961].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    
    # Washington post
    searches[8075] = []
    searches[8075].append('+AND+DATE+BEFORE+January+2+1991')
    for year in range(1991, 1999):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(1999, 2003):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+May+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+May+1+' + str(year) + '+AND+DATE+BEFORE+September+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+September+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2003, 2012):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+April+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+April+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+October+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+October+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    
    for year in range(2012, 2013):
        searches[8075].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+March+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+March+1+' + str(year) + '+AND+DATE+BEFORE+May+16+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+May+15+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+October+2+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+October+1+' + str(year) + '+AND+DATE+BEFORE+November+16+' + str(year))
        searches[8075].append('+AND+DATE+AFTER+November+15+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))



    # NYT
    searches[6742] = []
    searches[6742].append('+AND+DATE+BEFORE+January+1+1973')
    searches[6742].append('+AND+DATE+AFTER+January+1+1973+AND+DATE+BEFORE+January+2+1976')
    searches[6742].append('+AND+DATE+AFTER+January+1+1976+AND+DATE+BEFORE+June+2+1980')
    for year in range(1980, 1981):
        searches[6742].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+September+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+September+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(1981, 2004):
        searches[6742].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+May+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+May+1+' + str(year) + '+AND+DATE+BEFORE+September+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+September+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2004, 2013):
        searches[6742].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+March+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+March+1+' + str(year) + '+AND+DATE+BEFORE+May+16+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+May+15+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+October+2+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+October+1+' + str(year) + '+AND+DATE+BEFORE+November+16+' + str(year))
        searches[6742].append('+AND+DATE+AFTER+November+15+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    

    # St. Petersburg Times
    searches[11063] = []
    for year in range(1988, 2013):
        searches[11063].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[11063].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    

    # Philadelphia Inquirer
    searches[247189] = []
    for year in range(1994, 2003):
        searches[247189].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2003, 2013):        
        searches[247189].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[247189].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    




    # Atlanta Journal and Constitution
    searches[8379] = []
    for year in range(1991, 2013):
        searches[8379].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[8379].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    


    # Washington Post blogs
    searches[409005] = []
    searches[409005].append('+AND+DATE+BEFORE+January+2+2013')

    # Herald Sun
    searches[278130] = []
    searches[278130].append('+AND+DATE+BEFORE+January+2+1997')
    for year in range(1997, 2013):
        searches[278130].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    searches[278131] = []
    searches[278131].append('+AND+DATE+BEFORE+January+2+2013')

    # USA TODAY
    searches[8213] = []
    for year in range(1988, 1989):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+2))
    for year in range(1990, 1997):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))
    for year in range(2006, 2013):
        searches[8213].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))



    # NYT Blogs
    searches[379740] = []
    for year in range(2011, 2013):        
        searches[379740].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[379740].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    

    # Daily News
    searches[151550] = []
    for year in range(1995, 2013):
        searches[151550].append('+AND+DATE+AFTER+January+1+' + str(year) + '+AND+DATE+BEFORE+July+2+' + str(year))
        searches[151550].append('+AND+DATE+AFTER+July+1+' + str(year) + '+AND+DATE+BEFORE+January+2+' + str(year+1))    


    search_strings = []
    for csi in searches.keys():
        for date_string in searches[csi]:
            search = url_base + '/hottopics/lnacademic/?verb=sr&csi=' + str(csi) + '&sr=SUBJECT(marriage)+AND+GEOGRAPHIC(UNITED+STATES)' + date_string
            search_strings.append(search)

    return search_strings
