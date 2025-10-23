// // Dashboard JavaScript

// document.addEventListener('DOMContentLoaded', function() {
//     // Update date and time
//     updateDateTime();
//     setInterval(updateDateTime, 1000);

//     // Add animation to stat cards
//     animateStatCards();

//     // Mobile menu toggle (if needed)
//     setupMobileMenu();

//     // Setup tab switching
//     setupTabSwitching();
//     setupSubtabSwitching();

//     // Setup attendance system
//     setupAttendanceSystem();
// });

// function updateDateTime() {
//     const dateTimeElement = document.getElementById('dateTime');
//     if (!dateTimeElement) return;

//     const now = new Date();
//     const options = {
//         year: 'numeric',
//         month: 'long',
//         day: 'numeric',
//         hour: '2-digit',
//         minute: '2-digit',
//         second: '2-digit',
//         hour12: false
//     };

//     const jalaliDate = convertToJalali(now);
//     dateTimeElement.textContent = `${jalaliDate.year}/${String(jalaliDate.month).padStart(2, '0')}/${String(jalaliDate.day).padStart(2, '0')} - ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
// }

// function convertToJalali(d) {
//     const gy = d.getFullYear();
//     const gm = d.getMonth() + 1;
//     const gd = d.getDate();

//     let jy, jm, jd;
//     const g_d_n = 365 * gy + Math.floor((gy + 3) / 4) - Math.floor((gy + 99) / 100) + Math.floor((gy + 399) / 400) + gd;
//     for (jy = -61; jy <= 426; jy++) {
//         const j_d_n = 365 * jy + Math.floor((jy + 128) / 33) + Math.floor((jy + 3900 + 128) / 4) - Math.floor((jy + 3900 + 99) / 100) + Math.floor((jy + 3900 + 399) / 400);
//         if (g_d_n < j_d_n)
//             break;
//     }
//     jy--;
//     const a = g_d_n - (365 * jy + Math.floor((jy + 128) / 33) + Math.floor((jy + 3900 + 128) / 4) - Math.floor((jy + 3900 + 99) / 100) + Math.floor((jy + 3900 + 399) / 400));
//     if (a < 186) {
//         jm = 1 + Math.floor(a / 31);
//         jd = 1 + (a % 31);
//     } else {
//         jm = 7 + Math.floor((a - 186) / 30);
//         jd = 1 + ((a - 186) % 30);
//     }

//     return { year: jy, month: jm, day: jd };
// }

// function animateStatCards() {
//     const statCards = document.querySelectorAll('.stat-card');
//     statCards.forEach((card, index) => {
//         card.style.opacity = '0';
//         card.style.transform = 'translateY(20px)';
//         card.style.transition = `all 0.5s ease-out ${index * 0.1}s`;

//         setTimeout(() => {
//             card.style.opacity = '1';
//             card.style.transform = 'translateY(0)';
//         }, 100);
//     });
// }

// function setupTabSwitching() {
//     const tabNavBtns = document.querySelectorAll('.tab-nav-btn');
    
//     tabNavBtns.forEach(btn => {
//         btn.addEventListener('click', function() {
//             const tabName = this.getAttribute('data-tab');
            
//             // Remove active class from all tab buttons
//             tabNavBtns.forEach(b => b.classList.remove('active'));
            
//             // Add active class to clicked button
//             this.classList.add('active');
            
//             // Hide all tab contents
//             const tabContents = document.querySelectorAll('.dashboard-tabs .tab-content');
//             tabContents.forEach(content => content.classList.remove('active'));
            
//             // Show selected tab content
//             const selectedTab = document.getElementById(tabName + '-tab');
//             if (selectedTab) {
//                 selectedTab.classList.add('active');
                
//                 // Activate first subtab if exists
//                 activateFirstSubtab(selectedTab);
//             }
//         });
//     });
    
//     // Activate first tab on page load
//     const firstTabBtn = document.querySelector('.tab-nav-btn');
//     if (firstTabBtn) {
//         firstTabBtn.click();
//     }
// }

// function activateFirstSubtab(tabElement) {
//     const subtabBtns = tabElement.querySelectorAll('.subtab-btn');
//     const subtabContents = tabElement.querySelectorAll('.subtab-content');
    
//     // Deactivate all
//     subtabBtns.forEach(btn => btn.classList.remove('active'));
//     subtabContents.forEach(content => content.classList.remove('active'));
    
//     // Activate first
//     if (subtabBtns.length > 0) {
//         subtabBtns[0].classList.add('active');
//     }
//     if (subtabContents.length > 0) {
//         subtabContents[0].classList.add('active');
//     }
// }

// function setupSubtabSwitching() {
//     // For each tab, setup its subtabs
//     const tabContents = document.querySelectorAll('.dashboard-tabs .tab-content');
    
//     tabContents.forEach(tab => {
//         const subtabBtns = tab.querySelectorAll(':scope > .tab-header .subtab-btn');
//         const subtabContents = tab.querySelectorAll(':scope > .subtab-content');
        
//         subtabBtns.forEach(btn => {
//             btn.addEventListener('click', function(e) {
//                 e.preventDefault();
//                 const subtabName = this.getAttribute('data-subtab');
                
//                 // Remove active class from all subtab buttons in this tab
//                 subtabBtns.forEach(b => b.classList.remove('active'));
                
//                 // Add active class to clicked button
//                 this.classList.add('active');
                
//                 // Hide all subtab contents in this tab
//                 subtabContents.forEach(content => content.classList.remove('active'));
                
//                 // Show selected subtab content
//                 const selectedSubtab = document.getElementById(subtabName + '-subtab');
//                 if (selectedSubtab) {
//                     selectedSubtab.classList.add('active');
//                 }
//             });
//         });
//     });
// }

// function setupMobileMenu() {
//     // Add mobile menu toggle if needed
//     const sidebar = document.querySelector('.sidebar');
//     const dashboardMain = document.querySelector('.dashboard-main');

//     if (!sidebar) return;

//     // Create mobile menu button if screen is small
//     if (window.innerWidth <= 768) {
//         const menuBtn = document.createElement('button');
//         menuBtn.className = 'mobile-menu-btn';
//         menuBtn.innerHTML = '☰';
//         menuBtn.style.cssText = `
//             position: fixed;
//             top: 10px;
//             left: 10px;
//             width: 40px;
//             height: 40px;
//             background-color: #667eea;
//             color: white;
//             border: none;
//             border-radius: 0.5rem;
//             cursor: pointer;
//             z-index: 999;
//             font-size: 1.2rem;
//         `;

//         menuBtn.addEventListener('click', () => {
//             sidebar.classList.toggle('active');
//         });

//         document.body.appendChild(menuBtn);

//         // Close sidebar when clicking on main content
//         if (dashboardMain) {
//             dashboardMain.addEventListener('click', () => {
//                 sidebar.classList.remove('active');
//             });
//         }
//     }
// }

// // Table row hover effect
// document.addEventListener('DOMContentLoaded', function() {
//     const tableRows = document.querySelectorAll('.data-table tbody tr');
//     tableRows.forEach(row => {
//         row.addEventListener('mouseenter', function() {
//             this.style.backgroundColor = '#f0f4ff';
//         });
//         row.addEventListener('mouseleave', function() {
//             this.style.backgroundColor = '';
//         });
//     });
// });

// // Export table to CSV (utility function)
// function exportTableToCSV(tableName, filename) {
//     const csv = [];
//     const rows = document.querySelectorAll(tableName + ' tr');

//     rows.forEach(row => {
//         const cols = row.querySelectorAll('td, th');
//         const csvrow = Array.from(cols)
//             .map(col => {
//                 let text = col.textContent.trim();
//                 // Remove HTML tags
//                 text = text.replace(/<[^>]*>/g, '');
//                 return `"${text}"`;
//             })
//             .join(',');
//         csv.push(csvrow);
//     });

//     downloadCSV(csv.join('\n'), filename);
// }

// function downloadCSV(csv, filename) {
//     const csvFile = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
//     const link = document.createElement('a');
//     const url = URL.createObjectURL(csvFile);

//     link.setAttribute('href', url);
//     link.setAttribute('download', filename);
//     link.style.visibility = 'hidden';
//     document.body.appendChild(link);
//     link.click();
//     document.body.removeChild(link);
// }

// // Print functionality
// function printDashboard() {
//     window.print();
// }

// // Refresh dashboard data
// function refreshDashboard() {
//     location.reload();
// }

// // Add keyboard shortcuts
// document.addEventListener('keydown', function(e) {
//     // Ctrl/Cmd + R: Refresh
//     if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
//         e.preventDefault();
//         refreshDashboard();
//     }

//     // Ctrl/Cmd + P: Print
//     if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
//         e.preventDefault();
//         printDashboard();
//     }
// });

// // Dark mode toggle (optional)
// function toggleDarkMode() {
//     document.body.classList.toggle('dark-mode');
//     localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
// }

// // Check for dark mode preference
// if (localStorage.getItem('darkMode') === 'true') {
//     document.body.classList.add('dark-mode');
// }

// // ============================================
// // سیستم حضور و غیاب (Attendance System)
// // ============================================

// function setupAttendanceSystem() {
//     // فقط اگر تب حضور و غیاب وجود داشته باشد
//     const attendanceTab = document.getElementById('attendance-tab');
//     if (!attendanceTab) return;

//     // بارگذاری وضعیت حضور و غیاب
//     loadAttendanceStatus();
    
//     // بارگذاری تاریخچه حضور
//     loadAttendanceHistory();
    
//     // تنظیم دکمه‌های ورود و خروج
//     setupAttendanceButtons();
    
//     // بروزرسانی وضعیت هر ۳۰ ثانیه
//     setInterval(() => {
//         loadAttendanceStatus();
//         loadAttendanceHistory();
//     }, 30000);
// }

// function loadAttendanceStatus() {
//     const statusDiv = document.getElementById('attendanceStatus');
//     if (!statusDiv) return;

//     fetch('/api/attendance-status/')
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 // نمایش وضعیت
//                 statusDiv.innerHTML = `<p style="white-space: pre-line; font-size: 16px; color: #333;">${data.status_text}</p>`;
                
//                 // نمایش یا مخفی کردن دکمه‌ها
//                 const checkInBtn = document.getElementById('checkInBtn');
//                 const checkOutBtn = document.getElementById('checkOutBtn');
                
//                 if (checkInBtn) {
//                     checkInBtn.style.display = data.show_check_in ? 'block' : 'none';
//                 }
//                 if (checkOutBtn) {
//                     checkOutBtn.style.display = data.show_check_out ? 'block' : 'none';
//                 }
//             } else {
//                 statusDiv.innerHTML = `<p style="color: red; font-size: 14px;">⚠️ ${data.message}</p>`;
//             }
//         })
//         .catch(error => {
//             statusDiv.innerHTML = `<p style="color: red; font-size: 14px;">❌ خطا در بارگذاری: ${error.message}</p>`;
//         });
// }

// function loadAttendanceHistory() {
//     fetch('/api/attendance-history/')
//         .then(response => response.json())
//         .then(data => {
//             if (data.success) {
//                 // بروزرسانی جدول تاریخچه
//                 const tbody = document.getElementById('attendanceTable');
//                 if (tbody) {
//                     tbody.innerHTML = '';
//                     if (data.records.length === 0) {
//                         tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">هنوز رکوردی ثبت نشده است</td></tr>';
//                     } else {
//                         data.records.forEach(record => {
//                             const row = document.createElement('tr');
//                             row.innerHTML = `
//                                 <td>${record.date}</td>
//                                 <td>${record.check_in}</td>
//                                 <td>${record.check_out}</td>
//                                 <td>${record.work_duration}</td>
//                                 <td>${record.overtime}</td>
//                                 <td>${record.status}</td>
//                             `;
//                             tbody.appendChild(row);
//                         });
//                     }
//                 }

//                 // بروزرسانی آمار
//                 if (data.stats) {
//                     const totalDays = document.getElementById('totalDays');
//                     const totalHours = document.getElementById('totalHours');
//                     const totalOvertime = document.getElementById('totalOvertime');
                    
//                     if (totalDays) totalDays.textContent = data.stats.total_days;
//                     if (totalHours) totalHours.textContent = data.stats.total_hours;
//                     if (totalOvertime) totalOvertime.textContent = data.stats.total_overtime;
//                 }
//             }
//         })
//         .catch(error => {
//             console.error('خطا در بارگذاری تاریخچه:', error);
//         });
// }

// function setupAttendanceButtons() {
//     const checkInBtn = document.getElementById('checkInBtn');
//     const checkOutBtn = document.getElementById('checkOutBtn');
//     const messageBox = document.getElementById('actionMessage');

//     if (checkInBtn) {
//         checkInBtn.addEventListener('click', performCheckIn);
//     }

//     if (checkOutBtn) {
//         checkOutBtn.addEventListener('click', performCheckOut);
//     }
// }

// function performCheckIn() {
//     const messageBox = document.getElementById('actionMessage');
//     const btn = document.getElementById('checkInBtn');
    
//     // غیر فعال کردن دکمه
//     btn.disabled = true;
//     btn.style.opacity = '0.6';
    
//     fetch('/api/check-in/', {
//         method: 'POST',
//         headers: {
//             'X-CSRFToken': getCsrfToken(),
//             'Content-Type': 'application/json'
//         }
//     })
//     .then(response => response.json())
//     .then(data => {
//         showMessage(messageBox, data.message, data.success);
        
//         // بروزرسانی وضعیت
//         setTimeout(() => {
//             loadAttendanceStatus();
//             loadAttendanceHistory();
//         }, 1000);
//     })
//     .catch(error => {
//         showMessage(messageBox, `❌ خطا: ${error.message}`, false);
//     })
//     .finally(() => {
//         btn.disabled = false;
//         btn.style.opacity = '1';
//     });
// }

// function performCheckOut() {
//     const messageBox = document.getElementById('actionMessage');
//     const btn = document.getElementById('checkOutBtn');
    
//     // غیر فعال کردن دکمه
//     btn.disabled = true;
//     btn.style.opacity = '0.6';
    
//     fetch('/api/check-out/', {
//         method: 'POST',
//         headers: {
//             'X-CSRFToken': getCsrfToken(),
//             'Content-Type': 'application/json'
//         }
//     })
//     .then(response => response.json())
//     .then(data => {
//         if (data.success) {
//             showMessage(messageBox, `${data.message}\n⏰ خروج: ${data.check_out}\n⏱️ مدت کار: ${data.work_duration}\n⚡ اضافه‌کاری: ${data.overtime}`, true);
//         } else {
//             showMessage(messageBox, data.message, false);
//         }
        
//         // بروزرسانی وضعیت
//         setTimeout(() => {
//             loadAttendanceStatus();
//             loadAttendanceHistory();
//         }, 1000);
//     })
//     .catch(error => {
//         showMessage(messageBox, `❌ خطا: ${error.message}`, false);
//     })
//     .finally(() => {
//         btn.disabled = false;
//         btn.style.opacity = '1';
//     });
// }

// function showMessage(messageBox, message, isSuccess) {
//     if (!messageBox) return;
    
//     messageBox.style.display = 'block';
//     messageBox.className = 'message-box ' + (isSuccess ? 'success' : 'error');
//     messageBox.innerHTML = `<p style="white-space: pre-line; margin: 0;">${message}</p>`;
    
//     // اختیاری: مخفی کردن پیام بعد از ۵ ثانیه
//     setTimeout(() => {
//         messageBox.style.display = 'none';
//     }, 5000);
// }

// function getCsrfToken() {
//     const name = 'csrftoken';
//     let cookieValue = null;
//     if (document.cookie && document.cookie !== '') {
//         const cookies = document.cookie.split(';');
//         for (let i = 0; i < cookies.length; i++) {
//             const cookie = cookies[i].trim();
//             if (cookie.substring(0, name.length + 1) === (name + '=')) {
//                 cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
//                 break;
//             }
//         }
//     }
//     return cookieValue;
// }