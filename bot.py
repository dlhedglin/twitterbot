import tweepy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException
from time import sleep
import mysql.connector
from requests.exceptions import Timeout, ConnectionError
from requests.packages.urllib3.exceptions import ReadTimeoutError

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True,wait_on_rate_limit_notify=True)
currentFollowing = api.get_user('').friends_count
bannedusers = ['bot', 'spot']
search_terms = ['giveaway retweet', 'rt win', 'rt giveaway', 'retweet win', 'rt winning', 'retweet winning', 'giveaway winning', 'giving retweet']
driver = webdriver.Firefox()
driver.get('https://twitter.com/login')
driver.implicitly_wait(5)
element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "js-username-field")))
element.click()
element.send_keys('')
element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "js-password-field")))
element.click()
element.send_keys('')
sleep(1)
element.send_keys(Keys.RETURN)
sleep(3)
print("Logged into twitter")
mydb = mysql.connector.connect(
host="localhost",
user="root",
passwd="",
database = 'twitterdata'
)

mycursor = mydb.cursor()
def is_user_bot_hunter(username):
    clean_username = username.replace("0", "o")
    clean_username = clean_username.lower()
    for i in bannedusers:
        if i in clean_username:
            print('Skipping spam account')
            return True
        else:
            return False
def search(paramaters, type, amount):
    global currentFollowing
    for tweet in tweepy.Cursor(api.search, tweet_mode="extended", q = paramaters + ' -sugardaddy -sugarbaby -baby -sugar -home -vote -chek -click -filter:retweets -filter:replies -url:gleam -from:agus99914 -from:rt_goon -from:retweeejt -from:kakusan_RT -from:google_yahoo_rt -from:_aekkaphon -from:VOETBALSHIRTS16 -from:ClassicBet101 -from:tsgo_rt -from:ilove70315673 -from:followandrt2win -from:RodgerKieth -from:kogilligan -from:AbolyYT', result_type = type).items(amount):
        if mydb.is_connected() == 0:
            mydb.connect()
            print("reconnected")
        if(is_user_bot_hunter(tweet.user.name) == False):
            try:
                status = api.get_status(tweet.id)
                tweetText = tweet.full_text.lower()
                if currentFollowing > 4950:
                    mycursor.execute('SELECT username FROM followedusers ORDER BY id ASC LIMIT 1')
                    username = mycursor.fetchone()
                    try:
                        driver.get('https://twitter.com/' + username[0])
                        element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, "following-text")))
                        element.click()
                        print('Unfollowed: @' + username[0])
                        sleep(15)
                    except (TimeoutException, ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException) as ex:
                        print(str(ex))
                    mycursor.execute('DELETE FROM followedusers WHERE username = %s', (username[0], ))
                    mydb.commit()
                    currentFollowing -= 1
                if status.retweeted == False:
                    try:
                        print('\nTweet by: @' + tweet.user.screen_name)
                        driver.get('https://twitter.com/' + tweet.user.screen_name + '/status/' + tweet.id_str)
                        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "js-actionRetweet")))
                        element.click()
                        element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "retweet-action")))
                        element.click()
                        print('Retweeted the tweet')
                    except (TimeoutException, ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException) as ex:
                        print(str(ex))
                
                    if "follow" in tweetText or "#follow" in tweetText or "following" in tweetText or "#following" in tweetText:
                        if api.show_friendship(source_screen_name = '', target_screen_name = tweet.user.screen_name)[0].following == False:
                            try:
                                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "follow-button")))
                                element.click()
                                print('Followed: @' + tweet.user.screen_name)
                                currentFollowing += 1
                            except (TimeoutException, ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException) as ex:
                                print(str(ex))
                            try:
                                mycursor.execute('INSERT INTO followedusers(username) VALUES(%s)', (tweet.user.screen_name, ))
                                mydb.commit()
                                print(mycursor.rowcount, "record inserted.")
                            except mysql.connector.Error as err:
                                print("Something went wrong: {}".format(err))
                        else:
                            print("You already follow this user")
                    if 'like' in tweetText or '#like' in tweetText or 'favorite' in tweetText or '#favorite' in tweetText:
                        if status.favorited == False:
                            try:
                                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "js-actionFavorite")))
                                element.click()
                                print("liked the tweet")
                            except (TimeoutException, ElementNotVisibleException, ElementClickInterceptedException, ElementNotInteractableException) as ex:
                                print(str(ex))
                    sleep(60)
            except tweepy.TweepError as e:
                print(e.reason)
                if 'limit' in e.reason:
                    print('Sleeping 15 mins.....')
                    sleep(15 * 60)
            except StopIteration:
                break
            except (Timeout, ReadTimeoutError, ConnectionError) as exc:
                print(exc)
                sleep(60)
while True:
    for i in range(len(search_terms)):
        search(search_terms[i], 'popular', 20)
        search(search_terms[i], 'recent', 20)
    print('Sleeping 15 mins.....')
    sleep(15 * 60)
