logoutButton = document.getElementById('logoutButton');

const BASE_URL = 'http://127.0.0.1:8000/';
const URL_USER_AUTHENTICATE= "api/accounts/login/";
const URL_REFRESH_TOKEN="api/accounts/refresh/";

const miAPI = axios.create({
    baseURL: BASE_URL,
    withCredentials:true
});

miAPI.interceptors.response.use(function(response) {
  return response;
},function(error) {
    const originalReq = error.config;

    if ( error.response.status == 401 && !originalReq._retry && error.response.config.url != URL_USER_AUTHENTICATE ) {
      originalReq._retry = true;

      return axios.post(BASE_URL+URL_REFRESH_TOKEN, null, {
        withCredentials:true
      }).then((res) =>{
          if ( res.status == 200) {
              return axios(originalReq);
          }
        }).catch((error) => {window.location.href="../authentication/login.html"});
    }
    return Promise.reject(error);
});

logoutButton.addEventListener('click', function(e){
    miAPI.post(BASE_URL + 'api/accounts/logout/', null, {
        headers: {
          'Content-type': 'application/json; charset=UTF-8',
        },
        withCredentials: true,
      }
    )
    .then(function (response) {
      sessionStorage.setItem("showmsg", "Successfully logged-out!");
      window.location.replace("../authentication/login.html");
    })
    .catch(function (error) {
      // handle error
      // console.log(error);
    })
    .finally(function () {
      // always executed
    })
});

function initMap() {
  const directionsService = new google.maps.DirectionsService();
  const directionsRenderer = new google.maps.DirectionsRenderer();
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 8,
    center: { lat: 17.45, lng: 78.38 },
  });

  const startInput = document.getElementById("startLocation");
  const endInput = document.getElementById("endLocation");
  const autocompleteStart = new google.maps.places.Autocomplete(startInput);
  const autocompleteEnd = new google.maps.places.Autocomplete(endInput);

  directionsRenderer.setMap(map);

  const onSubmitHandler = function () {
    calculateAndDisplayRoute(directionsService, directionsRenderer, autocompleteStart, autocompleteEnd);
  };

  document.getElementById("submitBtn").addEventListener("click", onSubmitHandler);
}
  
function calculateAndDisplayRoute(directionsService, directionsRenderer, startLocation, endLocation) {
    directionsService
      .route({
        origin: {
          query: startLocation.getPlace().formatted_address,
        },
        destination: {
          query: endLocation.getPlace().formatted_address,
        },
        travelMode: google.maps.TravelMode.DRIVING,
      })
      .then((response) => {
        directionsRenderer.setDirections(response);
        start_lat = startLocation.getPlace().geometry.location.lat();
        start_lng = startLocation.getPlace().geometry.location.lng();
        miAPI.post(BASE_URL + 'api/cabs/find-nearest-cab/', {
            'start_lat': start_lat.toString(),
            'start_lng': start_lng.toString(),
          }, {
            headers: {
              'Content-type': 'application/json; charset=UTF-8',
            },
          }
        )
        .then(function (response) {
          console.log(response);
        })
        .catch(function (error) {
          // handle error
          // console.log(error);
        })
        .finally(function () {
          // always executed
        })
      })
      .catch((e) => window.alert("Directions request failed due to " + status));
}
  
window.initMap = initMap;
