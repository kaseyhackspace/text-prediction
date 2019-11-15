from flask import Flask, render_template
from flask_socketio import SocketIO
from flask_socketio import send, emit
import pickle
import json
import numpy as np
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

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
                'probability': list(best['probability']),
                'values': list(best['values'])
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

markov_model  = MarkovChain()
markov_model.load_model('markov_model.pickle')

@app.route('/')
def sessions():
    return render_template('client.html')

@socketio.on('connected')
def handle_connected(data):
    print(data)

@socketio.on('get_best')
def handle_get_best(data):
    
    best = markov_model.get_best(data['data'])
    emit('send_best',json.dumps(best))

if __name__ == '__main__':
    socketio.run(app)