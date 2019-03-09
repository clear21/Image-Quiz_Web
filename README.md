# Image-Quiz_Web

# Overview
複数のモデルの認識結果をもとに画像を当てるクイズアプリ  
※リポジトリ「Image-Quiz」をWebアプリ化したものです。(Django使用)  
　Image-Quiz : https://github.com/clear21/Image-Quiz

# Description
特定の画像に対して、複数のモデル（CNN）で認識をしていき、順に結果を提示します。  
提示された結果をもとに、何の画像かを当てるクイズです。  
10種類のものを分類できるモデルや、2種類しか分類できないモデルなど様々用意しており、  
様々なレベルのモデルを活かしてみました。

# How to Use
①フォルダ、ファイルを全てローカルにダウンロード（ダウンロード先の指定は特に無し）  
　[Clone or download] → [Download ZIP] → ZIPを展開  
②コマンドプロンプト、ターミナルを開き、manage.pyがあるフォルダをカレントディレクトリにする。  
③「python manage.py runserver」と入力し、実行する。  
④プロンプトに「Starting development server at http://127.0.0.1:8000/ 」と出力されたら、  
　http://127.0.0.1:8000/image_quiz/ にアクセス。  
