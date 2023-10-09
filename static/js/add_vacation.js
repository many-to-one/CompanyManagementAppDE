// After input a last date, the quantity of days will shows automatically
function sumDays(){
    var dateFrom = new Date(document.getElementById('dateFrom').value);
    var dateTo = new Date(document.getElementById('dateTo').value);
    const today = new Date();
    const currentYear = today.getFullYear();
    console.log('currentYear', currentYear)

    // Holidays
    const holidays = [
        `${currentYear}-01-01`,
        `${currentYear}-04-07`,
        `${currentYear}-04-10`,
        `${currentYear}-05-01`,
        `${currentYear}-05-18`,
        `${currentYear}-05-29`,
        `${currentYear}-10-03`,
        `${currentYear}-12-25`,
        `${currentYear}-12-26`,
    ];

    // This is a function that format date to the string we use 
    // to compare with strings in the holiday's list
    function formatDate(date) {
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    }

    function calculateWeekdays(dateFrom, dateTo) {
      var count = 0;
      var currentDate = new Date(dateFrom);

      while (currentDate <= dateTo) {
        // Check if the current day is not Sunday (0) or holidays
        if (
            currentDate.getDay() !== 0 && 
            !holidays.includes(formatDate(currentDate))
            ) {
          count++;
        }
        // Nex day by adding +1 number
        currentDate.setDate(currentDate.getDate() + 1);
      }
  
      return count;
    }

    var res = calculateWeekdays(dateFrom, dateTo)
    document.getElementById('days_planned').value = res
    console.log('res', res)
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