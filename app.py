import dash
import dash_core_components as dcc
import dash_html_components as html
import pickle

class NGram:

    def ngram(self, text, n=2):
        text_list = text.lower().split()
        grams = [tuple(text_list[index:index+n]) for index in range(0, len(text_list) - (n-1))]
        return grams

    def bigram(self, text):
        return self.ngram(text, n=2)

    def trigram(self, text):
        return self.ngram(text, n=3)

class MarkovChain:
    def __init__(self):
        self.model = {}
    
    def load_model(self,file):
        pickle_file = open(file,'rb')
        self.model = pickle.load(pickle_file)
        pickle_file.close()
    
    def calculate_probabilities(self):
        for key in self.model:
            total_sum = np.sum(self.model[key]['counts'])
            self.model[key]['probability'] = [x/total_sum for x in self.model[key]['counts']]
            
    def get_best(self,word,n=3):
        if word in self.model.keys():
            df = pd.DataFrame({
                'probability':list(self.model[word]['probability']),
                'values':list(self.model[word]['values'])
            })
            best = df.nlargest(n,'probability') 
            return {
                'probability': best['probability'],
                'values': best['values']
            }
        else:
            return None
        
    def train_model(self,text):
        
        ngram = NGram()
        
        bigrams = ngram.bigram(text)
        
        for bigram in bigrams:
            if bigram[0] not in self.model:
                self.model[bigram[0]]= {
                    'values': [bigram[1]],
                    'counts': [1],
                    'probability': []
                }
            else:
                if bigram[1] not in self.model[bigram[0]]['values']:
                    self.model[bigram[0]]['values'].append(bigram[1])
                    self.model[bigram[0]]['counts'].append(1)
                else:
                    index = self.model[bigram[0]]['values'].index(bigram[1])
                    self.model[bigram[0]]['counts'][index] = self.model[bigram[0]]['counts'][index] + 1
            
            self.calculate_probabilities()

markov_model = MarkovChain()
markov_model.load_model('markov_model.pickle')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Text Predictor'),

    html.Div(id='button-container',
    children=[
        html.Button('test1', id='recommendation1',style={'width': '33.33%'}, n_clicks_timestamp=0),
        html.Button('test2', id='recommendation2',style={'width': '33.33%'}, n_clicks_timestamp=0),
        html.Button('test3', id='recommendation3',style={'width': '33.33%'}, n_clicks_timestamp=0),
    ]),
    dcc.Textarea(
        id='text-area',
        placeholder='Enter a string...',
        value='',
        style={'width': '100%'}
    ),
    dcc.Interval(
        id='interval-component',
        interval=200, # in milliseconds
        n_intervals=0
    )
])

@app.callback(
    dash.dependencies.Output('text-area','value'),
    [
        dash.dependencies.Input('recommendation1','n_clicks_timestamp'),
        dash.dependencies.Input('recommendation2','n_clicks_timestamp'),
        dash.dependencies.Input('recommendation3','n_clicks_timestamp')
    ],
    [
        dash.dependencies.State('recommendation1','children'),
        dash.dependencies.State('recommendation2','children'),
        dash.dependencies.State('recommendation3','children'),
        dash.dependencies.State('text-area','value')
    ]
)
def choose_word(
    btn_timestamp1,
    btn_timestamp2,
    btn_timestamp3,
    btn1_value,
    btn2_value,
    btn3_value,
    text_area_value
    ):
    print(btn_timestamp1,btn_timestamp2,btn_timestamp3)
    tokens = text_area_value.split()
    if int(btn_timestamp1) > int(btn_timestamp2) and int(btn_timestamp1) > int(btn_timestamp3):
        last = btn1_value
    elif int(btn_timestamp2) > int(btn_timestamp1) and int(btn_timestamp2) > int(btn_timestamp3):
        last = btn2_value
    elif int(btn_timestamp3) > int(btn_timestamp1) and int(btn_timestamp3) > int(btn_timestamp2):
        last = btn2_value
    else:
        last = ''
    if tokens:
        tokens[-1] = last
    else:
        tokens = [last]
    msg = ' '.join(tokens)
    return msg

@app.callback(dash.dependencies.Output('button-container', 'children'),
              [dash.dependencies.Input('interval-component', 'n_intervals')],
              [dash.dependencies.State('text-area','value')]
              )
def update_buttons(n):

    return [
        html.Button('test1', id='recommendation1',style={'width': '33.33%'}, n_clicks_timestamp=0),
        html.Button('test2', id='recommendation2',style={'width': '33.33%'}, n_clicks_timestamp=0),
        html.Button('test3', id='recommendation3',style={'width': '33.33%'}, n_clicks_timestamp=0),
    ]

if __name__ == '__main__':
    app.run_server(debug=True)