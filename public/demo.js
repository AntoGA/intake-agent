'use strict';
const form=document.querySelector('#demo-form');
const next=document.querySelector('#next');
const stage=document.querySelector('#stage');
const title=document.querySelector('#result-title');
const body=document.querySelector('#result-body');
const events=document.querySelector('#events');
let step=0,failed=false;
function show(label,heading,message,button){stage.textContent=label;title.textContent=heading;body.textContent=message;next.hidden=!button;if(button)next.textContent=button;const li=document.createElement('li');li.textContent=label;events.append(li);}
function reset(){step=0;failed=false;events.replaceChildren();next.hidden=true;stage.textContent='Ожидание заявки';title.textContent='Здесь появится результат';body.textContent='Выберите источник и запустите пример.';for(const el of form.elements)el.disabled=false;}
form.addEventListener('submit',event=>{event.preventDefault();const request=document.querySelector('#request').value.trim();if(!request){document.querySelector('#request').focus();return;}reset();failed=document.querySelector('#failure').checked;const source=document.querySelector('#source').selectedOptions[0].text;for(const el of form.elements)el.disabled=true;step=1;show('Принято: '+source,'Заявка сохранена в демо',request,'Подготовить черновик');});
next.addEventListener('click',()=>{if(step===1&&failed){failed=false;show('Сбой обработки','Повтор доступен','В этом примере источник ответа временно недоступен. Заявка остаётся в очереди.','Повторить обработку');return;}if(step===1){step=2;show('Черновик готов','Нужна проверка сотрудника','Здравствуйте! Спасибо за обращение. Уточните желаемый результат, сроки и бюджет. После уточнения мы сможем оценить задачу.','Согласовать пример');}else if(step===2){step=3;show('Согласовано','Проверка завершена','Демонстрационный ответ согласован. Отправки клиенту нет. Для нового примера сбросьте демонстрацию.');}});
document.querySelector('#reset').addEventListener('click',reset);
