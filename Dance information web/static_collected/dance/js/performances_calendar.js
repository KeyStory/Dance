document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var modal = document.getElementById('performanceModal');
    var currentPerfId = null;
    var currentDate = new Date();
    var performances = [];
    
    var calendarSection = document.querySelector('.calendar-section');
    var artistId = calendarSection.dataset.artistId;
    var csrfToken = calendarSection.dataset.csrfToken;

    // 日历导航
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        refreshCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        refreshCalendar();
    });

    // 获取performances数据
    async function fetchPerformances() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        
        const response = await fetch(
            `/api/artist/${artistId}/performances?start=${firstDay.toISOString().split('T')[0]}&end=${lastDay.toISOString().split('T')[0]}`
        );
        performances = await response.json();
        refreshCalendar();
    }

    // 刷新日历
    function refreshCalendar() {
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        
        document.getElementById('currentMonth').textContent = 
            new Date(year, month).toLocaleDateString('default', { month: 'long', year: 'numeric' });

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const startingDay = firstDay.getDay();
        
        // 清空日历
        calendarEl.innerHTML = '';
        
        // 添加上个月的日期
        for (let i = 0; i < startingDay; i++) {
            const day = new Date(year, month, -startingDay + i + 1);
            addDayToCalendar(day, true);
        }
        
        // 添加当月日期
        for (let i = 1; i <= lastDay.getDate(); i++) {
            const day = new Date(year, month, i);
            addDayToCalendar(day, false);
        }
        
        // 添加下个月的日期填充最后一行
        const remainingDays = 42 - (startingDay + lastDay.getDate());
        for (let i = 1; i <= remainingDays; i++) {
            const day = new Date(year, month + 1, i);
            addDayToCalendar(day, true);
        }
    }

    // 添加日期到日历
    function addDayToCalendar(date, isOtherMonth) {
        const dayEl = document.createElement('div');
        dayEl.className = 'calendar-day' + 
                         (isOtherMonth ? ' other-month' : '') +
                         (isSameDay(date, new Date()) ? ' today' : '');
        
        dayEl.textContent = date.getDate();
        
        // 检查是否有performance
        const dateStr = date.toISOString().split('T')[0];
        const dayPerformances = performances.filter(p => p.performance_date === dateStr);
        
        if (dayPerformances.length > 0) {
            dayEl.classList.add('has-performance');
            dayEl.addEventListener('click', () => showPerformances(dayPerformances[0]));
        }
        
        calendarEl.appendChild(dayEl);
    }

    // 检查是否是同一天
    function isSameDay(date1, date2) {
        return date1.getDate() === date2.getDate() &&
               date1.getMonth() === date2.getMonth() &&
               date1.getFullYear() === date2.getFullYear();
    }

    // 显示performance详情
    function showPerformances(performance) {
        currentPerfId = performance.performance_id;
        document.getElementById('perf-title').textContent = performance.title;
        document.getElementById('perf-date').textContent = performance.performance_date;
        document.getElementById('perf-time').textContent = 
            `${performance.start_time} - ${performance.end_time}`;
        document.getElementById('perf-venue').textContent = performance.venue;
        document.getElementById('perf-participants').textContent = 
            performance.participants_number;
        document.getElementById('perf-status').textContent = performance.status;
        
        const attendanceStatus = document.getElementById('attendance-status');
        const attendanceDisplay = document.getElementById('attendance-status-display');
        
        if (attendanceStatus) {
            attendanceStatus.value = performance.attendance ? "1" : "0";
        }
        if (attendanceDisplay) {
            attendanceDisplay.textContent = performance.attendance ? 
                "Attending" : "Not Attending";
        }
        
        modal.style.display = "block";
    }

    // 关闭模态框
    document.querySelector('.btn-close').addEventListener('click', function(e) {
        /*e.preventDefault();  // 阻止默认行为
        e.stopPropagation(); // 阻止事件冒泡*/
        modal.style.display = "none";
    });

    // 更新出勤状态
    const updateAttendanceBtn = document.querySelector('.btn-update-attendance');
    if (updateAttendanceBtn) {
        updateAttendanceBtn.addEventListener('click', async () => {
            const attendance = 
                document.getElementById('attendance-status').value === "1";
            
            const response = await fetch(
                `/api/performance/${currentPerfId}/attendance`, {
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
                modal.style.display = "none";
                await fetchPerformances();
                const attendanceDisplay = 
                    document.getElementById('attendance-status-display');
                if (attendanceDisplay) {
                    attendanceDisplay.textContent = attendance ? 
                        "Attending" : "Not Attending";
                }
            }
        });
    }

    // 点击modal外部关闭modal
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }

    // 初始化日历
    fetchPerformances();
});