document.addEventListener('DOMContentLoaded', () => {
    const predictionForm = document.getElementById('prediction-form');
    const predictionResults = document.getElementById('prediction-results');
    const revenueChart = document.getElementById('revenue-chart').getContext('2d');

    // Backend API base URL
    const API_BASE_URL = '';  // Kosongkan karena kita menggunakan relative URL

    // Handle prediction form submission
    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log('Form submitted'); // Debug log

        const ternakBesar = parseFloat(document.getElementById('ternak-besar').value);
        const ternakKecil = parseFloat(document.getElementById('ternak-kecil').value);

        try {
            // Validasi input
            if (isNaN(ternakBesar) || isNaN(ternakKecil)) {
                throw new Error("Input harus berupa angka");
            }
            
            if (ternakBesar < 0 || ternakKecil < 0) {
                throw new Error("Jumlah ternak tidak boleh negatif");
            }

            console.log("Sending data:", { ternak_besar: ternakBesar, ternak_kecil: ternakKecil });

            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ternak_besar: ternakBesar,
                    ternak_kecil: ternakKecil
                })
            });

            // Log response untuk debug
            console.log("Response status:", response.status);
            const data = await response.json();
            console.log("Response data:", data);

            if (!response.ok) {
                throw new Error(data.message || `HTTP error! status: ${response.status}`);
            }

            if (data.status === 'success') {
                // Fungsi helper untuk mendapatkan arrow dan warna
                const getArrowAndColor = (value) => {
                    if (value >= 0) {
                        return {
                            arrow: '↑',
                            color: 'text-green-600'
                        };
                    } else {
                        return {
                            arrow: '↓',
                            color: 'text-red-600'
                        };
                    }
                };

                const predictionHtml = `
                    <div class="bg-green-100 text-green-800 p-4 rounded-md">
                        <h3 class="font-bold mb-2">Prediksi Pendapatan</h3>
                        
                        <!-- Tambahkan Target Harian -->
                        <p class="mb-2">
                            Target Harian: <span class="font-bold">Rp ${data.target_harian.toLocaleString('id-ID')}</span>
                        </p>
                        
                        <!-- Rata-rata Prediksi dan Defisit -->
                        <p class="flex items-center gap-2 mb-2">
                            Rata-rata Prediksi: 
                            <span class="${getArrowAndColor(data.avg_prediction).color} font-bold">
                                ${getArrowAndColor(data.avg_prediction).arrow} Rp ${Math.abs(data.avg_prediction).toLocaleString('id-ID')}
                            </span>
                        </p>
                        <p class="mb-4">
                            Status: <span class="font-bold ${data.avg_deficit > 0 ? 'text-red-600' : 'text-green-600'}">
                                ${data.avg_deficit > 0 ? 'KURANG' : 'TERCAPAI'} 
                                (${data.avg_deficit > 0 ? '-' : '+'} Rp ${Math.abs(data.avg_deficit).toLocaleString('id-ID')})
                            </span>
                        </p>

                        <!-- Prediksi per minggu -->
                        <h4 class="mt-4 font-semibold">Prediksi 4 Minggu Kedepan:</h4>
                        <div class="grid grid-cols-1 gap-2 mt-2">
                            ${data.predictions.map((pred, index) => `
                                <div class="flex items-center justify-between border-b py-2">
                                    <span>${pred.hari}, ${pred.tanggal}</span>
                                    <div class="text-right">
                                        <span class="${pred.defisit > 0 ? 'text-red-600' : 'text-green-600'} font-bold">
                                            Rp ${Math.abs(pred.nilai).toLocaleString('id-ID')}
                                        </span>
                                        <br>
                                        <span class="text-sm ${pred.defisit > 0 ? 'text-red-500' : 'text-green-500'}">
                                            ${pred.status} ${pred.defisit_rupiah}
                                        </span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
                predictionResults.innerHTML = predictionHtml;
                
                // Refresh grafik setelah prediksi berhasil
                setTimeout(fetchRevenueHistory, 1000);
            } else {
                throw new Error(data.message || 'Prediksi gagal');
            }
        } catch (error) {
            console.error('Error:', error); // Debug log
            predictionResults.innerHTML = `
                <div class="bg-red-100 text-red-700 p-4 rounded-md">
                    Gagal melakukan prediksi: ${error.message}
                </div>
            `;
        }
    });

    // Fetch revenue history
    async function fetchRevenueHistory() {
        try {
            const response = await fetch('/revenue_history');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Revenue history:', data); // Debug log

            if (data.status === 'success') {
                renderRevenueChart(data.history);
            }
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    }

    // Initial load
    fetchRevenueHistory();

    // Tambahkan fungsi ini sebelum fetchRevenueHistory
    function renderRevenueChart(history) {
        try {
            console.log("Data untuk chart:", history);

            // Destroy existing chart if any
            if (window.revenueChartInstance) {
                window.revenueChartInstance.destroy();
            }

            if (!history || history.length === 0) {
                console.log("Tidak ada data untuk ditampilkan");
                window.revenueChartInstance = new Chart(revenueChart, {
                    type: 'line',
                    data: {
                        labels: ['Tidak ada data'],
                        datasets: [{
                            label: 'Pendapatan',
                            data: [0],
                            borderColor: 'rgb(75, 192, 192)'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            title: {
                                display: true,
                                text: 'Belum ada data pendapatan',
                                font: { size: 16 }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: value => 'Rp ' + value.toLocaleString('id-ID')
                                }
                            }
                        }
                    }
                });
                return;
            }

            const labels = history.map(entry => {
                const date = new Date(entry.Tanggal);
                return date.toLocaleDateString('id-ID');
            });
            const revenues = history.map(entry => parseFloat(entry.Total_Pendapatan));

            console.log("Labels:", labels);
            console.log("Revenues:", revenues);

            window.revenueChartInstance = new Chart(revenueChart, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Pendapatan',
                        data: revenues,
                        borderColor: '#3B82F6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 6,
                        pointBackgroundColor: '#3B82F6',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: '#2563EB',
                        pointHoverBorderColor: '#fff',
                        pointHoverBorderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(0, 0, 0, 0.1)',
                                drawBorder: false
                            },
                            ticks: {
                                font: {
                                    size: 12,
                                    weight: '500'
                                },
                                padding: 10,
                                callback: value => ''
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: {
                                    size: 12,
                                    weight: '500'
                                },
                                padding: 10
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                padding: 20,
                                font: {
                                    size: 13,
                                    weight: '600'
                                }
                            }
                        },
                        tooltip: {
                            backgroundColor: 'rgba(0, 0, 0, 0.8)',
                            titleFont: {
                                size: 13,
                                weight: '600'
                            },
                            bodyFont: {
                                size: 12
                            },
                            padding: 12,
                            cornerRadius: 8,
                            callbacks: {
                                label: function(context) {
                                    return 'Pendapatan: Rp ' + context.raw.toLocaleString('id-ID');
                                }
                            }
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error rendering chart:', error);
        }
    }
});