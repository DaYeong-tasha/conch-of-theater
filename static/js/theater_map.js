class TheaterMap {
    constructor(mapContainerId, theaters, isMini = false) {
        this.theaters = theaters;
        this.currentMarkers = [];
        this.isMini = isMini;

        // 공통 초기화
        this.currentCircle = null;
        this.currentInfowindow = null;
        this.userMarker = null;
        this.userPosition = null;
        this.geocoder = new kakao.maps.services.Geocoder();
        this.places = new kakao.maps.services.Places();
        this.searchMarker = null;
        this.mapContainerId = mapContainerId;

        if (isMini) {
            this.showLocationModal();
        } else {
            this.initializeMap();
        }

        // window 객체에 함수 추가
        window.theaterMap = this;
        window.closeTheaterInfoWindow = function () {
            if (window.theaterMap) {
                window.theaterMap.closeCurrentInfoWindow();
            }
        }
    }

    // 위치 권한 모달 표시
    showLocationModal() {
        const modal = document.getElementById('locationModal');
        const allowBtn = document.getElementById('allowLocation');
        const denyBtn = document.getElementById('denyLocation');

        allowBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            this.initializeMap();
            this.initializeWithCurrentLocation();
        });

        denyBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            this.initializeMap();
            this.initializeWithKakaoHQ();
        });
    }

    // 카카오 판교 사옥으로 초기화하는 함수
    initializeWithKakaoHQ() {
        const kakaoHQ = new kakao.maps.LatLng(37.402056, 127.108212);
        this.map.setCenter(kakaoHQ);
        this.userPosition = kakaoHQ;

        if (this.userMarker) this.userMarker.setMap(null);
        this.userMarker = new kakao.maps.Marker({
            position: kakaoHQ,
            map: this.map,
            image: new kakao.maps.MarkerImage(
                'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
                new kakao.maps.Size(24, 35)
            )
        });

        this.filterMiniMapByRadius(5000);

        const radiusBtns = document.querySelectorAll('.radius-btn');
        radiusBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.radius === '5000') {
                btn.classList.add('active');
            }
        });
    }

    // 지도 초기화
    initializeMap() {
        const container = document.getElementById(this.mapContainerId);
        const options = {
            center: new kakao.maps.LatLng(37.566826, 126.9786567),
            level: this.isMini ? 7 : 7
        };
        this.map = new kakao.maps.Map(container, options);

        if (this.isMini) {
            this.map.setZoomable(true);
            this.map.setDraggable(true);
        } else {
            this.getCurrentLocation();
            this.updateTheaterList(this.theaters);
            this.showMarkersForTheaters(this.theaters);
        }
    }

    // 현재 위치로 초기화하는 함수
    initializeWithCurrentLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const lat = position.coords.latitude;
                    const lng = position.coords.longitude;
                    const currentPos = new kakao.maps.LatLng(lat, lng);

                    this.map.setCenter(currentPos);

                    if (this.userMarker) this.userMarker.setMap(null);
                    this.userMarker = new kakao.maps.Marker({
                        position: currentPos,
                        map: this.map,
                        image: new kakao.maps.MarkerImage(
                            'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
                            new kakao.maps.Size(24, 35)
                        )
                    });

                    this.userPosition = currentPos;
                    this.filterMiniMapByRadius(5000);
                },
                (error) => {
                    console.error('Geolocation error:', error);
                    this.initializeWithKakaoHQ();
                }
            );
        } else {
            this.initializeWithKakaoHQ();
        }
    }

    showLoading() {
        if (this.isMini) return;
        document.getElementById('loadingSpinner').style.display = 'block';
    }

    hideLoading() {
        if (this.isMini) return;
        document.getElementById('loadingSpinner').style.display = 'none';
    }

    // 미니맵용 마커 
    showMiniMapMarkers(radius = 5000) {
        this.clearMarkers();

        this.theaters.forEach(theater => {
            this.geocoder.addressSearch(theater.adres, (result, status) => {
                if (status === kakao.maps.services.Status.OK) {
                    const coords = new kakao.maps.LatLng(result[0].y, result[0].x);

                    // 현재 위치가 있을 경우 거리 계산
                    if (this.userPosition) {
                        const distance = this.calculateDistance(
                            this.userPosition.getLat(), this.userPosition.getLng(),
                            coords.getLat(), coords.getLng()
                        );

                        // 설정된 반경 내의 극장만 표시
                        if (distance > radius) return;

                        theater.distance = distance;
                    }

                    const marker = new kakao.maps.Marker({
                        position: coords,
                        map: this.map
                    });

                    // 미니맵용 모달 정보창
                    const overlay = this.createMiniInfoWindow(theater, coords);

                    kakao.maps.event.addListener(marker, 'click', () => {
                        if (this.currentInfowindow) {
                            this.currentInfowindow.setMap(null);
                        }
                        // 줌 레벨 설정 후 부드럽게 이동
                        this.map.setLevel(3);
                        this.map.panTo(coords);
                        overlay.setMap(this.map);
                        this.currentInfowindow = overlay;
                    });

                    this.currentMarkers.push(marker);
                }
            });
        });

        // 마커가 모두 표시된 후 지도 범위 재설정
        setTimeout(() => {
            if (this.currentMarkers.length > 0) {
                const bounds = new kakao.maps.LatLngBounds();
                this.currentMarkers.forEach(marker => {
                    bounds.extend(marker.getPosition());
                });
                this.map.setBounds(bounds);
            }
        }, 1000);
    }

    // 미니맵 전용 정보창 생성
    createMiniInfoWindow(theater, coords) {
        let distanceText = '';
        if (this.userPosition) {
            const distance = this.calculateDistance(
                this.userPosition.getLat(), this.userPosition.getLng(),
                coords.getLat(), coords.getLng()
            );
            distanceText = `<div class="distance">현재 위치에서 ${(distance / 1000).toFixed(1)}km</div>`;
        }

        const infoContent = `
            <div class="mini-info-window">
                <div class="info-header">
                    <h4>${theater.fcltynm}</h4>
                    <button class="close-btn" onclick="closeTheaterInfoWindow()">✕</button>
                </div>
                <div class="info-body">
                    <p>${theater.adres}</p>
                    ${distanceText}
                    <div class="action-buttons">
                        <button onclick="window.open('https://map.kakao.com/link/to/${theater.fcltynm},${coords.getLat()},${coords.getLng()}')">
                            길찾기
                        </button>
                    </div>
                </div>
            </div>
        `;

        return new kakao.maps.CustomOverlay({
            content: infoContent,
            position: coords,
            xAnchor: 0.5,
            yAnchor: 1.3
        });
    }

    // 반경 변경 시 호출되는 함수
    filterMiniMapByRadius(radius) {
        if (!this.isMini) return;

        // radius 파라미터가 없으면 기본값 5000 사용
        const searchRadius = radius || 5000;

        if (this.currentCircle) this.currentCircle.setMap(null);

        // 현재 위치 기준 반경 원 표시
        if (this.userPosition) {
            this.currentCircle = new kakao.maps.Circle({
                center: this.userPosition,
                radius: searchRadius,
                strokeWeight: 1,
                strokeColor: '#00a0e9',
                strokeOpacity: 0.1,
                strokeStyle: 'solid',
                fillColor: '#00a0e9',
                fillOpacity: 0.1
            });
            this.currentCircle.setMap(this.map);
        }

        // 해당 반경 버튼 활성화
        const radiusBtns = document.querySelectorAll('.radius-btn');
        radiusBtns.forEach(btn => {
            btn.classList.remove('active');
            if (parseInt(btn.dataset.radius) === searchRadius) {
                btn.classList.add('active');
            }
        });

        this.showMiniMapMarkers(searchRadius);
    }

    clearMarkers() {
        this.currentMarkers.forEach(marker => marker.setMap(null));
        this.currentMarkers = [];
        if (this.currentInfowindow) {
            this.currentInfowindow.setMap(null);
            this.currentInfowindow = null;
        }
    }

    closeCurrentInfoWindow() {
        if (this.currentInfowindow) {
            this.currentInfowindow.setMap(null);
            this.currentInfowindow = null;
        }
    }

    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 6371000;
        const dLat = this.toRad(lat2 - lat1);
        const dLon = this.toRad(lon2 - lon1);
        const lat1Rad = this.toRad(lat1);
        const lat2Rad = this.toRad(lat2);

        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
            Math.sin(dLon / 2) * Math.sin(dLon / 2) *
            Math.cos(lat1Rad) * Math.cos(lat2Rad);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }

    toRad(value) {
        return value * Math.PI / 180;
    }

    getCurrentLocation() {
        if (this.isMini) return;
        if (navigator.geolocation) {
            this.showLoading();
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    this.userPosition = new kakao.maps.LatLng(
                        position.coords.latitude,
                        position.coords.longitude
                    );

                    if (this.userMarker) this.userMarker.setMap(null);
                    this.userMarker = new kakao.maps.Marker({
                        position: this.userPosition,
                        map: this.map,
                        image: new kakao.maps.MarkerImage(
                            'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/markerStar.png',
                            new kakao.maps.Size(24, 35)
                        )
                    });

                    this.map.setCenter(this.userPosition);
                    this.filterTheatersByRadius();
                    this.hideLoading();
                },
                (error) => {
                    this.hideLoading();
                    if (error.code === error.PERMISSION_DENIED) {
                        alert('위치 정보 제공을 허용하면 주변 공연장을 더 쉽게 찾을 수 있습니다.');
                    } else {
                        console.error('Geolocation error:', error);
                        alert('현재 위치를 가져올 수 없습니다.');
                    }
                }
            );
        }
    }

    searchPlace() {
        if (this.isMini) return;
        const searchText = document.getElementById('searchInput').value;
        if (!searchText.trim()) return;

        this.showLoading();
        this.places.keywordSearch(searchText, (result, status) => {
            if (status === kakao.maps.services.Status.OK) {
                const place = result[0];
                const coords = new kakao.maps.LatLng(place.y, place.x);

                if (this.searchMarker) this.searchMarker.setMap(null);

                this.searchMarker = new kakao.maps.Marker({
                    position: coords,
                    map: this.map
                });

                this.map.setCenter(coords);
                this.userPosition = coords;
                this.filterTheatersByRadius();
            } else {
                alert('검색 결과를 찾을 수 없습니다.');
            }
            this.hideLoading();
        });
    }

    filterTheatersByRadius() {
        if (!this.userPosition) {
            alert('현재 위치를 가져올 수 없습니다.');
            return;
        }

        const radius = parseInt(document.getElementById('radiusSelect')?.value || 5000);
        if (this.currentCircle) this.currentCircle.setMap(null);

        this.currentCircle = new kakao.maps.Circle({
            center: this.userPosition,
            radius: radius,
            strokeWeight: 1,
            strokeColor: '#00a0e9',
            strokeOpacity: 0.1,
            strokeStyle: 'solid',
            fillColor: '#00a0e9',
            fillOpacity: 0.1
        });
        this.currentCircle.setMap(this.map);

        this.geocodeAllTheaters(this.theaters, (geocodedTheaters) => {
            const nearbyTheaters = geocodedTheaters
                .filter(theater => theater.distance <= radius)
                .sort((a, b) => a.distance - b.distance);

            this.updateTheaterList(nearbyTheaters);
            this.showMarkersForTheaters(nearbyTheaters);
        });
    }

    updateTheaterList(theaters) {
        if (this.isMini) return;
        const listContainer = document.getElementById('theaterList');
        const countElement = document.getElementById('theaterCount');
        if (!listContainer || !countElement) return;

        listContainer.innerHTML = '';
        countElement.textContent = theaters.length;

        if (theaters.length === 0) {
            listContainer.innerHTML = `
                <div class="no-results">
                    <p>주변에 공연장이 없습니다.</p>
                    <p>검색 반경을 늘려보세요!</p>
                </div>
            `;
            return;
        }

        theaters.forEach(theater => {
            const li = document.createElement('li');
            li.className = 'theater-item';
            let html = `
                <div class="theater-name">${theater.fcltynm}</div>
                <div class="theater-address">${theater.adres}</div>
                ${theater.telno ? `<div class="theater-tel">☎ ${theater.telno}</div>` : ''}
            `;

            if (this.userPosition && theater.distance) {
                html += `
                    <div class="distance">
                        현재 위치에서 ${(theater.distance / 1000).toFixed(1)}km
                    </div>
                `;
            }

            li.innerHTML = html;
            li.onclick = () => {
                this.geocoder.addressSearch(theater.adres, (result, status) => {
                    if (status === kakao.maps.services.Status.OK) {
                        const coords = new kakao.maps.LatLng(result[0].y, result[0].x);
                        this.map.setCenter(coords);
                        this.map.setLevel(3);
                    }
                });
            };

            listContainer.appendChild(li);
        });
    }
}