const searchButton = document.querySelector('.but');
const cardsRow = document.querySelector('.cards-row');
const cityInput = document.querySelector('.vvid input[placeholder="📍Місто"]');
const medicineInput = document.querySelector('.vvid input[placeholder="💊Препарат"]');
const resultBlock = document.querySelector('#resultBlock');
const saveButton = document.querySelector('.btn-save');

let lastPharmacies = [];
const apiBaseUrl = window.API_BASE_URL || '/api';

function buildCard(index, pharmacy) {
	const card = document.createElement('div');
	card.className = 'card new-card';
	card.innerHTML = `
		<h4>${index}. Аптека "${pharmacy.legal_entity_name}"</h4>
		<p>📍${pharmacy.division_addresses}, ${pharmacy.division_settlement}</p>
		<p>📞${pharmacy.division_phone}</p>
		<div class="card-footer">
			<div>
				<p>Тип видачі:</p>
				<p>${pharmacy.division_type}</p>
			</div>
		</div>
	`;
	return card;
}

async function fetchPharmacies(city, medicine) {
	try {
		const response = await fetch(
			`${apiBaseUrl}/top-pharmacies?city=${encodeURIComponent(city)}&medical_program=${encodeURIComponent(medicine)}`
		);
		if (!response.ok) {
			throw new Error(`API відповів зі статусом ${response.status}`);
		}
		return await response.json();
	} catch (error) {
		console.error('Помилка:', error);
		return [];
	}
}

async function renderResults() {
	const city = cityInput.value.trim();
	const medicine = medicineInput.value.trim();

	if (!city || !medicine) return;

	cardsRow.innerHTML = '<p>Завантаження...</p>';
	resultBlock.classList.remove('hidden');

	const pharmacies = await fetchPharmacies(city, medicine);

	lastPharmacies = pharmacies;
	cardsRow.innerHTML = '';

	const fragment = document.createDocumentFragment();
	pharmacies.slice(0, 3).forEach((pharmacy, index) => {
		fragment.appendChild(buildCard(index + 1, pharmacy));
	});

	cardsRow.appendChild(fragment);
}

searchButton.addEventListener('click', function () {
	renderResults();
});

saveButton.addEventListener('click', function () {
	const blob = new Blob([JSON.stringify(lastPharmacies, null, 2)], { type: 'application/json' });
	const url = URL.createObjectURL(blob);

	const link = document.createElement('a');
	link.href = url;
	link.download = 'pharmacies_report.json';
	link.click();

	URL.revokeObjectURL(url);
});