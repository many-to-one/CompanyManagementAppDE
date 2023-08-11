
// var currentDate = new Date();
// var month = cDate.toLocaleString("default", { month: "long" });
// var day = cDate.getDate()
var djangovar = "{{message.timestamp}}"
var currentDate = new Date();
if (djangovar == currentDate){
    alert('+')
}else{
    alert(djangovar)
}
document.write("<p>" + currentDate + "</p>")
