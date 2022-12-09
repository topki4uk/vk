import requests
import json
from marked import main as mark
import os

style = '''
<style>
body {
font-size:28;
}
  a {
  text-decoration: none;
  color:#2f61e0;
  }
   thead {
    background: #f5e8d0; /* Цвет фона заголовка */
   }
   td, th {
    padding: 5px; /* Поля в ячейках */
    border: 1px solid #333; /* Параметры рамки */
   }
   
  table {
  font-size:18px;
  font-family:Segoe UI;
  border-collapse: collapse;
  width: 80%;
  margin: auto;
  margin-bottom: 50px;
  }
  
  .closed {
  background: red;
  color: white;
  }
  
  .open {
  background: green;
  color: white;
  margin: 0;
  }
  
  .ones {
  background: #00FFFF;
  }
  
  .full {
  background: gold;
  }
</style>
'''


try:
    with open('vk_token.json') as file:
        try:
            access_token = json.load(file)['key']
        except json.decoder.JSONDecodeError:
            print('Vk токен не найден!')
except FileNotFoundError:
    with open('vk_token.json', 'w') as file:
        print('Создан файл vk_token.json')


def get_users_id(id):
    url = 'https://api.vk.com/method/{}'.format('users.get')
    response = requests.get(url, params={'user_ids': id,
                                         'fields': 'schools,occupation,screen_name,photo_200',
                                         'access_token': access_token, 'v': 5.131, 'lang': 'ru'}).json()

    try:
        response = response['response']
        return response
    except KeyError:
        print('error')


def main():
    url = 'https://api.vk.com/method/{}'.format('friends.get')

    try:
        user = get_users_id(input('Введите id пользователя:\n'))[0]
    except TypeError:
        return 0

    response = requests.get(url, params={'user_id': user['id'],
                                         'count': 1000, 'access_token': access_token, 'v': 5.131}).json()

    friends_list = ','.join(list(map(str, response['response']['items'])))
    friends_list = get_users_id(friends_list)

    for i in range(len(friends_list)):
        for j in range(i, len(friends_list)):
            if friends_list[i]['last_name'] > friends_list[j]['last_name']:
                friends_list[i], friends_list[j] = friends_list[j], friends_list[i]

    count = 1
    flag = False
    mark()
    with open('marked.json', 'r') as f:
        s = json.load(f)

    data = {
        'full_name': [],
        'photo': [],
        'is_open': [],
        'screen_name': [],
        'id': [],
        'schools': []
    }

    for i in friends_list:
        schools = []
        if 'deactivated' not in i.keys():
            if True:
                if 'occupation' in i.keys():
                    schools += [i['occupation']['name'].strip()]

                if 'schools' in i.keys():
                    schools += [j['name'].strip() for j in i['schools']]

                schools = ', '.join(schools)

                full_name = i['last_name'] + ' ' + i['first_name']

                if i['last_name'] in s.keys():
                    marked = 'ones'
                    if i['first_name'] == s[i['last_name']]:
                        marked = 'full'
                else:
                    marked = ''

                data['full_name'].append((full_name, marked))
                data['is_open'].append(i['is_closed'])
                data['screen_name'].append(i['screen_name'])
                data['schools'].append('---' if schools == '' else schools)
                data['id'].append(i['id'])
                data['photo'].append(i['photo_200'])

    with open('table.html', 'w', encoding='utf-8') as table:
        table.writelines('<meta charset="utf-8">\n')
        table.writelines(style+'\n')

        table.writelines('У пользователя {} {} найдено {} друзей'.format(user['first_name'],
                                                          user['last_name'],
                                                          response['response']['count']))
        table.writelines(
            '''
            <table>
            <thead>
            <tr style="text-align: right;">
            <th>№</th>
            '''
        )

        for param in data:
            table.writelines('<th>'+param+'</th>\n')

        table.writelines(
            '''
            </tr>
            </thead>
            <tbody>
            '''
        )

        for i in range(len(data['full_name'])):
            table.writelines('<tr class="{}">'.format(data['full_name'][i][1]))
            table.writelines('<th>{}</th>'.format(i+1))
            table.writelines(' <td><a href="https://vk.com/{}">{}</a></td>'.format(data['screen_name'][i], str(data['full_name'][i][0])))
            table.writelines('<td><img src="{}"></td>'.format(data['photo'][i]))
            table.writelines('<td class="{}">{}</td>'.format('closed' if data['is_open'][i] else 'open', 'Закрытый' if data['is_open'][i] else 'Открытый'))
            table.writelines('<td>{}</td>'.format(data['screen_name'][i]))
            table.writelines('<td>{}</td>'.format(data['id'][i]))
            table.writelines('<td>{}</td>'.format(str(data['schools'][i])))
            table.writelines('</tr>')

        table.writelines('</tbody>\n</table>')

    os.system('table.html')


if __name__ == '__main__':
    main()
