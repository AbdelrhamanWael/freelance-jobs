function adminlogout() {
    window.location.href = '../index.html';
}

  new Chart(document.getElementById('studentGrowthChart'), {
      type: 'line',
      data: {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        datasets: [{
          label: 'New Students',
          data: [5, 12, 19, 25, 32, 40],
          borderColor: '#243a6b',
          backgroundColor: 'rgba(36,58,107,0.2)',
          fill: true,
          tension: 0.3
        }]
      }
      
    });

    // Enrollments (Bar Chart)
    new Chart(document.getElementById('enrollmentsChart'), {
      type: 'bar',
      data: {
        labels: ['History', 'Language', 'Philosophy', 'Math'],
        datasets: [{
          label: 'Enrollments',
          data: [30, 45, 20, 15],
          backgroundColor: ['#d4af37','#243a6b','#f5deb3','#3a4a63']
        }]
      }
    });

    // Completion Rates (Pie Chart)
    new Chart(document.getElementById('completionChart'), {
      type: 'pie',
      data: {
        labels: ['Completed', 'In Progress', 'Dropped'],
        datasets: [{
          data: [70, 20, 10],
          backgroundColor: ['#4caf50','#ff9800','#f44336']
        }]
      }
    });





  