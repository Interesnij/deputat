
function case_news_wall(pk) {
  link_ = window.XMLHttpRequest ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP');
  link_.open('GET', "/notify/new_wall/" + pk + "/", true);
  link_.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

  link_.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          lenta = document.body.querySelector('.news_stream');
          elem = link_.responseText;
          new_post = document.createElement("span");
          new_post.innerHTML = elem;
          lenta.prepend(new_post);
          document.body.querySelector(".news_empty") ? document.body.querySelector(".news_empty").style.display = "none" : null}}
  link_.send()
}

if (!document.body.querySelector(".anon_avatar")){
  // подключаем сокеты только для зарегистрированных пользователей
notify = document.body.querySelector(".resent_notify");
document.body.querySelector(".userpic") ? request_user_id = document.body.querySelector(".userpic").getAttribute("data-pk") : request_user_id = 0
notify.innerHTML ? (notify_count = notify.innerHTML.replace(/\s+/g, ''), notify_count = notify_count*1): notify_count = 0;

ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
ws_path = ws_scheme + '://' + window.location.host + ":8443/notify/";
webSocket = new channels.WebSocketBridge();
webSocket.connect(ws_path);

webSocket.socket.onmessage = function(e){ console.log(e.data); };
webSocket.socket.onopen = function () {console.log("Соединение установлено!")};
webSocket.socket.onclose = function () {console.log("Соединение прервано...")};

webSocket.listen(function (event) {
  switch (event.key) {
      case "notification":
        if (event.recipient_id == request_user_id){
          notify_count += 1;
          notify.innerHTML = notify_count;
          console.log("теперь кол-во уведов - " + notify_count);
          new Audio('/static/audio/apple/stargaze.mp3').play();
        }
        break;

      case "wall":
            if (event.name == "user_wall"){
              // появление новых записей на стене, сваязанных с пользователями (например, действия челов разной направленности)
              case_user_wall()
            }
            else if (event.name == "news_wall"){
              // появление новых записей на главной стене
              if (document.body.querySelector(".news_stream")) {case_news_wall(event.id)}
            }
          break;
      case "message":
        if (event.creator_id != request_user_id){
          console.log("уведомления сообщений, звуки, отрисовка созданных элементов для участников чата");
        }
        break;

    default:
      console.log('error: ', event);
      break;
  }
})
}
