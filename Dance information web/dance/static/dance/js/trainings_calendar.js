document.addEventListener('DOMContentLoaded', function() {
    // Training Calendar Variables
    var trainingCalendarEl = document.getElementById('trainingCalendar');
    var trainingModal = document.getElementById('trainingModal');
    var currentTrainingId = null;
    var currentTrainingDate = new Date();
    var trainings = [];

    var calendarSection = document.querySelector('.calendar-section');
    var artistId = calendarSection.dataset.artistId;
    var csrfToken = calendarSection.dataset.csrfToken;

    // Training Calendar Navigation
    document.getElementById('prevMonthTraining').addEventListener('click', () => {
        currentTrainingDate.setMonth(currentTrainingDate.getMonth() - 1);
        refreshTrainingCalendar();
    });

    document.getElementById('nextMonthTraining').addEventListener('click', () => {
        currentTrainingDate.setMonth(currentTrainingDate.getMonth() + 1);
        refreshTrainingCalendar();
    });

    // Fetch Trainings
    async function fetchTrainings() {
        const year = currentTrainingDate.getFullYear();
        const month = currentTrainingDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        const response = await fetch(
            `/api/artist/${artistId}/trainings?start=${firstDay.toISOString().split('T')[0]}&end=${lastDay.toISOString().split('T')[0]}`
        );
        trainings = await response.json();
        refreshTrainingCalendar();
    }

    // Refresh Training Calendar
    function refreshTrainingCalendar() {
        const year = currentTrainingDate.getFullYear();
        const month = currentTrainingDate.getMonth();
        
        document.getElementById('currentMonthTraining').textContent = 
            new Date(year, month).toLocaleDateString('default', { month: 'long', year: 'numeric' });

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startingDay = firstDay.getDay();
        
        trainingCalendarEl.innerHTML = '';
        
        for (let i = 0; i < startingDay; i++) {
            const day = new Date(year, month, -startingDay + i + 1);
            addDayToTrainingCalendar(day, true);
        }
        
        for (let i = 1; i <= lastDay.getDate(); i++) {
            const day = new Date(year, month, i);
            addDayToTrainingCalendar(day, false);
        }
        
        const remainingDays = 42 - (startingDay + lastDay.getDate());
        for (let i = 1; i <= remainingDays; i++) {
            const day = new Date(year, month + 1, i);
            addDayToTrainingCalendar(day, true);
        }
    }

    // Add Day to Training Calendar
    function addDayToTrainingCalendar(date, isOtherMonth) {
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day' + 
                         (isOtherMonth ? ' other-month' : '') +
                         (isSameDay(date, new Date()) ? ' today' : '');
        
        dayEl.textContent = date.getDate();
        
        const dateStr = date.toISOString().split('T')[0];
        const dayTrainings = trainings.filter(t => t.training_date === dateStr);
        
        if (dayTrainings.length > 0) {
            dayEl.classList.add('has-performance');
            dayEl.addEventListener('click', () => showTraining(dayTrainings[0]));
        }
        
        trainingCalendarEl.appendChild(dayEl);
    }

    // 检查是否是同一天
    function isSameDay(date1, date2) {
        return date1.getDate() === date2.getDate() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getFullYear() === date2.getFullYear();
    }

    // Show Training Details
    function showTraining(training) {
        currentTrainingId = training.training_id;
        document.getElementById('training-title').textContent = training.title;
        document.getElementById('training-date').textContent = training.training_date;
        document.getElementById('training-time').textContent = 
            `${training.start_time} - ${training.end_time}`;
        document.getElementById('training-venue').textContent = training.venue;
        document.getElementById('training-participants').textContent = 
            training.participants_number;
        document.getElementById('training-status').textContent = training.status;
        
        const attendanceStatus = document.getElementById('training-attendance-status');
        const attendanceDisplay = document.getElementById('training-attendance-status-display');
        
        if (attendanceStatus) {
            attendanceStatus.value = training.attendance ? "1" : "0";
        }
        if (attendanceDisplay) {
            attendanceDisplay.textContent = training.attendance ? 
                "Attending" : "Not Attending";
        }
        
        trainingModal.style.display = "block";
    }

    // Training Modal Close Button
    document.querySelector('.btn-close-training').addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        trainingModal.style.display = "none";
    });

    // Update Training Attendance
    const updateTrainingAttendanceBtn = document.querySelector('#trainingModal .btn-update-attendance');
    if (updateTrainingAttendanceBtn) {
        updateTrainingAttendanceBtn.addEventListener('click', async () => {
            const attendance = 
                document.getElementById('training-attendance-status').value === "1";
            
            const response = await fetch(
                `/api/training/${currentTrainingId}/attendance`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({
                        artist_id: artistId,
                        attendance: attendance
                    })
                }
            );
            
            const data = await response.json();
            if (data.success) {
                await fetchTrainings();
                const attendanceDisplay = 
                    document.getElementById('training-attendance-status-display');
                if (attendanceDisplay) {
                    attendanceDisplay.textContent = attendance ? 
                        "Attending" : "Not Attending";
                }
            }
        });
    }

    // Close Training Modal on Outside Click
    trainingModal.addEventListener('click', function(e) {
        if (e.target === trainingModal) {
            e.preventDefault();
            trainingModal.style.display = "none";
        }
    });

    // ESC Key to Close Training Modal
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && trainingModal.style.display === 'block') {
            e.preventDefault();
            trainingModal.style.display = "none";
        }
    });

    // Initialize Training Calendar
    fetchTrainings();
});