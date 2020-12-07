from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth

import pandas as pd 
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from ast import literal_eval
from sklearn.metrics.pairwise import linear_kernel
import warnings
import json
# from IPython.display import Image, HTML
warnings.filterwarnings('ignore')

just_searched = pd.DataFrame()
# Create your views here.
def home(request):
    if request.method == 'POST':
        auth.logout(request)
        return render(request, 'home.html')
    else:
        return render(request, 'home.html', {'name':'nice'})

def about(request):
    return render(request, 'about.html')

def details(request):
    return render(request, 'movieDetails.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(username=username,password=password)
        if user is not None:
            auth.login(request, user)
            return render(request, 'account/user.html')
        else:
            return render(request, 'login.html', {'error': 'Invalid Credentials.'})
    else:
        return render(request, 'login.html')

def loginUser(request):
    return render(request, 'account/user.html')

def logout(request):
    return render(request, 'account/logout.html')

# def signup(request):
#     return render(request, 'signup.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'note': 'username already taken.'})
        elif User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'note': 'email already exists.'})
        else:
            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
            user.save()
            return render(request, 'login.html', {'note': 'New user created.'})
    else:
        return render(request, 'signup.html')

def recommend(request):
    return render(request, 'recommend.html')

def movie(request):
    return render(request, 'movie.html')

def add(request):

    val1 = int(request.POST['num1'])
    val2 = int(request.POST['num2'])
    res = val1 * val2
    return render(request, 'result.html', {'result':res})


def Data_cleaning(imdb):
    gen=[]
    genres=[]
    cleaning_cols = ['genres','spoken_languages','cast','crew','production_companies','keywords']
    for c in cleaning_cols:    
        imdb[c] = imdb[c].apply(literal_eval)

        for x in range(len(imdb[c])):
            gen=[]
            for i in imdb[c][x]:
                gen.append(i['name'])
            imdb[c][x] = gen
    return imdb

def data_sorting(imdb, movies):
    imdb = imdb.sort_values(['vote_count','vote_average'], ascending=[False, False]).groupby('title_x').head()
    C= imdb['vote_average'].mean()
    vote_counts = imdb[imdb['vote_count'].notnull()]['vote_count'].astype('int')
    m= vote_counts.quantile(0.70)
    imdb_mat = imdb[(imdb['vote_count'] >= m) & (imdb['vote_count'].notnull()) & (imdb['vote_average'].notnull())][['title_x', 'vote_count', 'vote_average', 'popularity', 'genres','overview']]
    imdb_mat['vote_count'] = imdb['vote_count'].astype('int')
    imdb_mat['vote_average'] = imdb['vote_average'].astype('int')

    return imdb
    
def get_recommendations_content_base(request):

    movies = pd.read_csv('./csv/tmdb_5000_movies.csv',index_col=False)
    credits = pd.read_csv('./csv/tmdb_5000_credits.csv',index_col=False)
    ids= pd.read_csv('./csv/IDS.csv')
    ids['id'] = ids['id'].astype(int)
    poster = pd.read_csv('./csv/MovieGenre.csv',encoding='ISO-8859-1')
    credits = credits.rename(columns ={'movie_id':'id'})
    imdb = pd.merge(movies,credits,on='id')
    imdb = pd.merge(imdb,ids,on='id')
    imdb = pd.merge(imdb,poster,on='imdbId')


    title = request.POST['title']
    imdb = Data_cleaning(imdb)
    # print(imdb.head(5))
    imdb = data_sorting(imdb, movies)
    links_small = pd.read_csv('./csv/links_small.csv')
    links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype('int')
    titles=[]
    search = []
    titles=list(imdb['title_x'])
    for t in titles:
        if title.lower() in t.lower():
            title = t
            print(title)
            break
    
    global just_searched
    just_searched = just_searched.append(imdb[imdb['title_y'] == title])
    smd = imdb[imdb['id'].isin(links_small)]
    smd['tagline'] = smd['tagline'].fillna('')
    smd['description'] = smd['overview'] + smd['tagline']
    smd['description'] = smd['description'].fillna('')
    tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
    tfidf_matrix = tf.fit_transform(smd['description'])
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    smd = smd.reset_index()
    titles = smd['title_y']
    indices = pd.Series(smd.index, index=smd['title_y'])
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    movie_indices = [i[0] for i in sim_scores]
    smd = smd.rename(columns ={'Imdb Link':'imdb_link'})
    # print(smd.iloc[movie_indices][['Title','Poster','imdb_link','popularity']].head(10))

    recom = smd.iloc[movie_indices][['Title','Poster','imdb_link','popularity','IMDB_Score']].head(10).to_json(orient ='records') 
    data = [] 
    data = json.loads(recom)

    searched = just_searched[['Title','Poster']].to_json(orient ='records')
    data1 = [] 
    data1 = json.loads(searched)
    context = {'d': data, 'searched': data1, 'title': title}
    # context = {'d': data, 'title': title}
    # context1 = {'searched': data1}


    return render(request, 'result.html', context)
    # return (list(smd[smd['title_x'] == titles.iloc[movie_indices[0]]]['genres'])[0][0]),(imdb[['id','Poster']].iloc[movie_indices])


def build_chart(request):
    movies = pd.read_csv('./csv/tmdb_5000_movies.csv',index_col=False)
    credits = pd.read_csv('./csv/tmdb_5000_credits.csv',index_col=False)
    ids= pd.read_csv('./csv/IDS.csv')
    ids['id'] = ids['id'].astype(int)
    poster = pd.read_csv('./csv/MovieGenre.csv',encoding='ISO-8859-1')
    credits = credits.rename(columns ={'movie_id':'id'})
    imdb = pd.merge(movies,credits,on='id')
    imdb = pd.merge(imdb,ids,on='id')
    imdb = pd.merge(imdb,poster,on='imdbId')

    imdb = Data_cleaning(imdb)
    # print(imdb.head(5))
    imdb = data_sorting(imdb, movies)

    genre = request.POST['genre']
    percentile=0.80
    s = imdb.apply(lambda x: pd.Series(x['genres']),axis=1).stack().reset_index(level=1, drop=True)
    s.name = 'genre'
    gen_md = imdb.drop('genres', axis=1).join(s)
    df = gen_md[gen_md['genre'] == genre]
    vote_counts = df[df['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = df[df['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(percentile)
    qualified = df[(df['vote_count'] >= m) & (df['vote_count'].notnull()) & (df['vote_average'].notnull())][['title_x', 'vote_count', 'vote_average', 'popularity','Poster','Imdb Link']]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')

    qualified['wr'] = qualified.apply(lambda x: (x['vote_count']/(x['vote_count']+m) * x['vote_average']) + (m/(m+x['vote_count']) * C), axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(250)
    qualified = qualified.rename(columns ={'Imdb Link':'imdb_link'})

    print(pd.DataFrame(qualified[['title_x','Poster','imdb_link','popularity','vote_count']]).head(10))

    recom = pd.DataFrame(qualified[['title_x','Poster','imdb_link','popularity','vote_count']]).head(10).to_json(orient ='records') 
    data = [] 
    data = json.loads(recom)
    context = {'d': data, 'title': genre}

    return render(request, 'result.html', context)


