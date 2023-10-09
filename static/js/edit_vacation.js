// After input a last date, the quantity of days will shows automatically
function sumDays(){
    var dateFrom = new Date(document.getElementById('dateFrom').value);
    var dateTo = new Date(document.getElementById('dateTo').value);
    
    function calculateWeekdays(dateFrom, dateTo) {
      var count = 0;
      var currentDate = new Date(dateFrom);

      while (currentDate <= dateTo) {
        // Check if the current day is not Sunday (0)
        if (currentDate.getDay() !== 0) {
          count++;
        }
        currentDate.setDate(currentDate.getDate() + 1);
      }
  
      return count;
    }
    var res = calculateWeekdays(dateFrom, dateTo)
    document.getElementById('days_planned').value = res
}

// Changing the option on 'z powodu siły wyższej', the form will be changed
var sel = document.getElementById('select');
var out = document.getElementById('output');
var steel = document.getElementById('steel');

function changeOption() {
  var selectedOption = sel.value;
  if (selectedOption === 'z powodu siły wyższej') {
    out.innerHTML = 

    '<div class="vacations_mini_cont">' +
        '<p>Od:</p>' +
        '<input name="v_from" id="dateFrom" type="date" class="vacations_input" value="{{date}}" >' +
    '</div>' +

    '<div class="vacations_mini_cont">' +
        '<p>Do:</p>' +
        '<input name="v_to" id="dateTo" type="date" class="vacations_input" value="{{date}}" oninput="sumDays()">' +
    '</div>' +

    '<div class="vacations_mini_cont">' +
      '<p>Liczba godzin urlopu:</p>' +
      '<input type="text" name="days_planned" id="days_planned" class="vacations_input" value="1">' +
    '</div>';
    
    steel.style.display = 'none';
  } else {
    out.innerHTML = '';
    steel.style.display = 'block';
  }
}