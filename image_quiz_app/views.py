from django.shortcuts import render
from django.http import HttpResponse

import os
from keras.models import load_model
import numpy as np
import cv2
import random
from time import sleep
import json
#from PIL import Image

#■変数_START-----------------------------------------------------
#このpgmファイルの格納フォルダ
#※getcwd：プロジェクトのフォルダ直下（アプリフォルダの格納フォルダ）
this_pgm_folder = os.path.join(os.getcwd() , 'image_quiz_app') 
folder_to_stat_folders = os.path.join(this_pgm_folder , 'static' , 'image_quiz_app')

#画像格納先フォルダ
#※注意：画像ファイル名は、 「"正解ラベル名"+"_"+"～.～"」 とすること。
img_folder = os.path.join(folder_to_stat_folders , 'image')

#モデルの格納先フォルダ
model_folder = os.path.join(folder_to_stat_folders , 'model')

#モデル適用結果(json)の格納先フォルダ
#モデル適用結果のjsonファイル名は 「ap_[given_img_file].json」
result_model_apply_folder = os.path.join(folder_to_stat_folders , 'result_model_apply')

#ラベル
cifar10_labels = np.array([
    'airplane',
    'automobile',
    'bird',
    'cat',
    'deer',
    'dog',
    'frog',
    'horse',
    'ship',
    'truck'])

#画像ファイルとラベルの辞書
img_label_dict = {}
img_folder_flist = os.listdir(img_folder)
for file_name in img_folder_flist:
    img_label_dict[file_name] = file_name.split('_')[0]

#選択肢の候補（cifar10のラベル、取り込む画像に存在するラベル、その他）
choice_candidate = list(cifar10_labels) + ['Sandwich Man(Comedian)'
                                              , 'shark'
                                              , 'monkey'
                                              , 'Pico Taro']

#使用するモデル（この順にモデルを使用するため、難度を考慮し、出力候補が少ない順にする。）
model_list = [
    'model_0_2.hdf5'
    , 'model_3_5.hdf5'
    , 'model_4_7.hdf5'
    , 'model_0_1_8_9.hdf5'
    , 'model_2_3_4_5_6_7.hdf5'
    , 'model_0_1_2_3_4_5_6_7_8_9.hdf5'
]

#読み込む祭のサイズ
size = (32 , 32)

#モデル番号(初期値は 0、各モデル結果を出した後 +1　し、最後のモデルを判定)
curr_model_no = 0

#home画面から「開始」ボタンを押下したときに 1 となってゲーム開始と判断
game_start_flg = 0

#回答した番号
ans_no = None

#問題とする画像、正解ラベル
given_img_file , ans_label = None , None

#各モデルの適用結果
list_result_of_models = []

#選択肢
choice_labels = {}

#ゲームスタート時の your_ans
start_your_ans = 99999

#■変数_END-----------------------------------------------------

#■関数_START------------------------------------------------------

#画像のリサイズ、正規化
#引数：対象の画像（cv2オブジェクト）、リサイズ後のサイズ（タプル）
def img_resize_normalize(img , size):
    #リサイズ
    img_resize = cv2.resize(img , size)
    
    #正規化
    img_resize_normalize = img_resize / 255
    
    return img_resize_normalize

#問題選択肢の生成
#引数：選択肢の数、正解ラベル、選択肢の候補（ラベルのリスト）
#戻り値：{1:ラベル名1 , 2:ラベル名2 , …}
def gen_answer_choice(choice_num , ans_label , choice_candidate):
    #第三引数の選択肢の候補から正解を除外
    #※参照渡しを防ぐためにスライス記法
    choice_candidate_rem_answer = choice_candidate[:]
    choice_candidate_rem_answer.remove(ans_label)
    
    #選択肢に出すラベル
    choice_labels_tmp = [ans_label] + random.sample(choice_candidate_rem_answer , choice_num - 1)
    
    choice_labels = {}
    for_max = len(choice_labels_tmp)
    for i in range(for_max):
        choice_labels[i] = random.choice(choice_labels_tmp)
        choice_labels_tmp.remove(choice_labels[i])
    
    return choice_labels

#特定画像の各モデル適用結果(テキストのリスト)を出力 
#引数：画像ファイル名、モデルのリスト
#戻り値：特定画像の各モデル適用結果(テキストのリスト)
def result_of_models_for_given_img(given_img_file , model_list):
    list_result_of_models = []
    
    #画像のオブジェクト化、リサイズ
    os.chdir(img_folder)
    img = cv2.imread(given_img_file)
    img = img_resize_normalize(img , size)
    
    #モデル適用
    os.chdir(model_folder)
    for i in range(len(model_list)):
        #モデルのファイル名
        model_file = model_list[i]
        
        #モデルの出力対象のリスト（cifar10のラベルリストのインデックスのリスト）
        gen_labels_num_tmp = model_file.replace('model_' , '').replace('.hdf5' , '').split('_')
        gen_labels_num = list(map(lambda x : int(x) , gen_labels_num_tmp))
        
        #モデルの出力対象のリスト（ラベル名のリスト）
        #（参考）モデルの出力は、cifar10_labelsの順になっている。
        #　　　　(例：dog,catが出力対象なら、pred[*][0]がdogの確率、pred[*][1]がcatの確率)
        model_labels_list = np.array(cifar10_labels)[gen_labels_num]
        
        #予測
        model = load_model(model_file)
        preds = model.predict(np.array([img]) , verbose = 0)
        
        #予測結果の出力テキスト
        #text_pred = ''
        list_text_pred = []
        for j in range(len(preds[0])):
            #text_pred += '\n' + model_labels_list[j] + '：' + str(round(preds[0][j] * 100 , 1) ) + '%'
            list_text_pred.append(model_labels_list[j] + '：' + str(round(preds[0][j] * 100 , 1) ) + '%')
        
        list_result_of_models.append(list_text_pred)
    
    return list_result_of_models

#問題とする画像(+正解ラベル)をランダムで出力
#引数：ファイル名がキーにラベル名を値とする辞書（img_label_dict）
#引数：画像ファイル、正解ラベル
def random_img_and_label(img_label_dict):
    selected_key = random.choice(list(img_label_dict.keys()))
    given_img_file = selected_key
    ans_label = img_label_dict[selected_key]
    return given_img_file , ans_label

#ゲーム用パラメータ初期化
def init_param():
    global curr_model_no , game_start_flg , ans_no , given_img_file , ans_label , list_result_of_models , start_your_ans , choice_labels , img_folder 
    #モデル番号(初期値は 0、各モデル結果を出した後 +1　し、最後のモデルを判定)
    curr_model_no = 0
    #home画面から「開始」ボタンを押下したときに 1 となってゲーム開始と判断
    game_start_flg = 0
    #回答した番号
    ans_no = None
    #問題とする画像、正解ラベル
    given_img_file , ans_label = None , None
    #各モデルの適用結果
    list_result_of_models = []
    #選択肢
    choice_labels = {}

#◆jsonファイルで保存
#引数：保存対象オブジェクト、ファイルのフルパス
def save_as_json(obj , file_full_path):
    json_fname_with_extension = file_full_path
    fw = open(json_fname_with_extension , 'w')
    json.dump(obj , fw , indent = 4)
    fw.close()

#◆jsonファイルを取得
#引数：対象ファイルのフルパス
def import_json(file_full_path):
    fr = open(file_full_path , 'r')
    f = json.load(fr)
    fr.close()
    return f

#■関数_END-----------------------------------------------------

# Create your views here.
def index(request):
    global curr_model_no , game_start_flg , ans_no , given_img_file , ans_label , list_result_of_models , start_your_ans , choice_labels , img_folder 
    params = {
            'title':'Hello/Index',
            'msg':'テスト！！',
            'goto':'/game/99999/'
            #'goto':'/game/' + str(start_your_ans) + '/'
            #'goto':'game/?start=1'
            }
    return render(request , 'image_quiz_app/index.html' , params)

def game(request , your_ans): #your_ans = 99999 :スタート時を意味する
    global curr_model_no , game_start_flg , ans_no , given_img_file , ans_label , list_result_of_models , start_your_ans , choice_labels , img_folder 
    params = {}
    params['your_ans'] = your_ans
    params['your_ans_name'] = None #あなたの回答した番号の対象名称
    params['answer'] = '' #正解
    params['open_answer_flg'] = 0 #正解を表示するときは 1
    params['result'] = None #回答が正解と合っているときは 1 はずれの場合は　0
    params['list_result_of_models'] = None #各モデルの結果をリストで保持。各モデル結果は　選択肢毎に結果テキストをリストで保持。
    params['choice_labels'] = None
    params['given_img_file_path'] = None
    params['start_your_ans'] = start_your_ans
    
    print('your_ans:' , your_ans)
    print('start_your_ans:' , start_your_ans)
    print('exact:' , your_ans==start_your_ans)
    
    #ゲームスタート(本関数の第二引数のデフォルト)の時はパラメータを初期化
    if your_ans == start_your_ans:
        print('----start init_param-------')
        init_param()
        print('----finish init_param-------')
    
    #始めに問題と正解ラベル、各モデル適用結果、選択肢　を取得
    if curr_model_no == 0:
        #問題とする画像、正解ラベル
        given_img_file , ans_label = random_img_and_label(img_label_dict)
        
        print('given_img_file is gotten')
        
        #モデル適用結果
        #すでに結果を保持していたら、それを使う。
        model_ap_file_name = 'ap_' + given_img_file.replace('.png' , '') + '.json'
        model_ap_file_full_path = os.path.join(result_model_apply_folder , model_ap_file_name)
        print('model_ap_file_full_path')
        print(model_ap_file_full_path)
        if os.path.exists(model_ap_file_full_path):
            list_result_of_models = import_json(model_ap_file_full_path)
            
            print('list_result_of_models of dump is loaded')
            
        else:
            #各モデル適用結果
            list_result_of_models = result_of_models_for_given_img(given_img_file , model_list)
            
            print('list_result_of_models is gotten')
            
            #保存
            save_as_json(list_result_of_models , model_ap_file_full_path)
            
            print('list_result_of_models of dump is gotten')
        
        print('list_result_of_models is gotten')
        
        #選択肢作成
        choice_labels = gen_answer_choice(len(model_list) + 1 , ans_label , choice_candidate)
    else:
        #あなたの回答した番号の対象名称
        params['your_ans_name'] = choice_labels[params['your_ans']]
        
        print('your_ans_name is gotten.')
        
        #正解
        params['answer'] = ans_label
        
        print('answer is gotten.')
        
        #回答が正解と合っているか確認
        if params['your_ans_name'] == params['answer']:
            params['result'] = 1
            params['open_answer_flg'] = 1
    
    print('data for start is gotten')
    
    #1モデル～現在のモデルまでの結果を表示させる
    params['list_result_of_models'] = list_result_of_models[:curr_model_no + 1]
    
    #選択肢
    params['choice_labels'] = choice_labels.items()
    
    #対象画像のフルパス
    params['given_img_file_path'] = os.path.join('image_quiz_app' , 'image' , given_img_file)
    
    #全モデル結果を出している場合は終了
    if curr_model_no == len(model_list):
        params['open_answer_flg'] = 1
        params['list_result_of_models'] = list_result_of_models[:curr_model_no]
    else:
        curr_model_no += 1
        if params['open_answer_flg'] == 1:
            #今まで表示していた分だけにする。
            params['list_result_of_models'] = list_result_of_models[:curr_model_no - 1]        
    
    print('Preparing finish')
    
    print('*' * 10)
    for key , val in params.items():
        if key in ('choice_labels'):
            continue
        print(key , ':' , val)
    print('*' * 10)
    
    return render(request , 'image_quiz_app/game.html' , params)

#def game_start(request):
#    global curr_model_no , game_start_flg , ans_no , given_img_file , ans_label , list_result_of_models
#    #ゲーム用パラメータ初期化
#    init_param()
#    #ゲーム開始
#    return game(request)