import logging
from datetime import datetime
from sqlalchemy.orm import sessionmaker

from model import Post, WordSearch, PType,  Base, create_engine


engine = create_engine('sqlite:///base.db', echo = True)

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)


def createSession():
    Session = sessionmaker()
    return Session(bind=engine)


def createDB(engine=engine):
    Base.metadata.create_all(engine)
    logger.info('Create database: {}'.format(engine))


def addWordsSearch(word):
    session = createSession()
    word_db = WordSearch()
    word_db.text = word
    session.add(word_db)

    try:
        session.commit()
    except:
        session.rollback()
        logger.error('WordSearch add fail.')
    finally:
        session.close()


def createDBPost(post):
    dbpost = Post()

    dbpost.title = post.title
    dbpost.url = post.url
    dbpost.ptype = PType(post.ptype)
    #dbpost.tier = post.tier
    dbpost.duration = post.duration
    dbpost.posted_time = datetime.strptime(post.posted_time, '%Y-%m-%dT%H:%M:%S%z')
    #dbpost.tags = post.tags
    dbpost.description = post.description
    dbpost.proposal = post.proposal
    dbpost.payment = 'Payment verified' == post.verified
    dbpost.spent = post.spent
    dbpost.location = post.location
    dbpost.feedback = post.feedback

    return dbpost


def createOrSkip(session, post, word):
    instance = session.query(Post).filter_by(url=post.url).first()
    if not instance:
        word_db = session.query(WordSearch).filter_by(text=word).first()
        dbpost = createDBPost(post)
        dbpost.word = word_db
        session.add(dbpost)

    else:
        logger.debug('Post skipped: {}'.format(post))


def addPosts(posts, word):
    logger.info('Posts saving in database: {}'.format(len(posts)))
    session = createSession()

    for post in posts:
        createOrSkip(session, post, word)

    try:
        session.commit()
        logger.info('Database commit.')
    except:
        session.rollback()
        logger.critical('Database roolback')

    session.close()
    logger.debug('Database closed.')


def getWordsSearch():
    logger.debug('Get search worlds.')
    session = createSession()
    word_db = session.query(WordSearch).all()
    return [w.text for w in word_db]


def getAllPosts():
    session = createSession()
    posts = session.query(Post).all()
    session.close()
    return [post.to_json() for post in posts]
