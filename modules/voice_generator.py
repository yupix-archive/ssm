import subprocess

import configparser

from main import Jtalk_Bin_Path, Dic_Path, Voice_Path, Spped, Output_wav_name

input_file = './tmp/input.txt'  # ファイルの指定
csv_header = ['server_id', 'before', 'after']

config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

def creat_wav(inputText):
    # TODO: 2020/11/22 辞書を追加

    with open(input_file, 'w', encoding='UTF-8') as file:
        file.write(inputText)

    command = '{c} -x {x} -m {m} -r {r} -ow {ow} {input_file}'

    args = {'c': Jtalk_Bin_Path, 'x': Dic_Path, 'm': Voice_Path, 'r': Spped, 'ow': Output_wav_name, 'input_file': input_file}

    cmd = command.format(**args)
    print(cmd)

    subprocess.run(cmd, shell=True)
    return True


if __name__ == '__main__':
    creat_wav('テスト音声です')
