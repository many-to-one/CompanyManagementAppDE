// CHART

document.addEventListener('DOMContentLoaded', function() {

    // Retrieve the data from the Django view
    var total_payment = JSON.parse(document.getElementById('total_payment').textContent);
    var total_fuel = JSON.parse(document.getElementById('total_fuel').textContent);
    var total_coffee_food = JSON.parse(document.getElementById('total_coffee_food').textContent);
    var total_phone_costs = JSON.parse(document.getElementById('total_phone_costs').textContent);
    var total_material_costs = JSON.parse(document.getElementById('total_material_costs').textContent);
    var subcontractors_sum = JSON.parse(document.getElementById('subcontractors_sum').textContent);

    var values = [
        total_payment,
        total_fuel,
        total_coffee_food,
        total_phone_costs,
        total_material_costs,
        subcontractors_sum,
    ]
    var labels = [
        'Pensje',
        'Paliwo',
        'Kawa/Posiłki',
        'Telefon',
        'Koszty materiałów',
        'Pomocnik/Podwykonawca',
    ]
    // Create the pie chart using Chart.js
    var ctx = document.getElementById('myChart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#9fadcc',
                    '#212A3E',
                    '#394867',
                    '#485268',
                    '#697b8c',
                    '#697b9c',
                ]
            }]
        },
    });
});

