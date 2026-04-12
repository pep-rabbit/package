const searchButton = document.querySelector('.but');
const cardsRow = document.querySelector('.cards-row');
const cityInput = document.querySelector('.vvid input[placeholder="📍Місто"]');
const medicineInput = document.querySelector('.vvid input[placeholder="💊Препарат"]');

const pharmacyNames = [
	'Подорожник',
	'Аптека №123',
	'Бажаємо Здоров’я',
	'АНЦ',
	'Мед-сервіс',
	'Фармсфера',
	'Добра Аптека'
];

const streets = [
	'вул. Хрещатик, 10',
	'вул. Саксаганського, 25',
	'просп. Перемоги, 84',
	'вул. Велика Васильківська, 19',
	'вул. Шевченка, 7'
];

function getRandomItem(list) {
	return list[Math.floor(Math.random() * list.length)];
}

function getRandomPhone() {
	return '+380 44 ' + String(100 + Math.floor(Math.random() * 900)) + ' ' + String(1000 + Math.floor(Math.random() * 9000));
}

function buildCard(index, city, medicine) {
	const name = getRandomItem(pharmacyNames);
	const street = getRandomItem(streets);

	const card = document.createElement('div');
	card.className = 'card new-card';
	card.innerHTML = `
		<h4>${index}. Аптека "${name}"</h4>
		<p>📍${street}, ${city}</p>
		<p>📞${getRandomPhone()}</p>
		<div class="card-footer">
			<div>
				<p>Тип видачі:</p>
				<p>Повною мірою безплатно</p>
			</div>
		</div>
	`;
	return card;
}

function renderResults() {
	const city = cityInput.value.trim() || 'Київ';
	const medicine = medicineInput.value.trim() || 'Еналаприл';

	cardsRow.innerHTML = '';

	const fragment = document.createDocumentFragment();

	for (let i = 1; i <= 3; i++) {
		fragment.appendChild(buildCard(i, city, medicine));
	}

	cardsRow.appendChild(fragment);
}

searchButton.addEventListener('click', function () {
	renderResults();
});

