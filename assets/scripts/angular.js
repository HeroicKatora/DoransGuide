var dataModule = angular.module('doransData', ['ngResource']);

dataModule.factory('Stats', ['$resource',
	function($resource) {
		return $resource('/data/:region/:patch/:map/:queue/:elo/:champion/:item/:role/:lane/data.json',
			{
				region: 'ANY',
				patch: 'ANY',
				map: 'ANY',
				queue: 'ANY',
				champion: 'ANY',
				item: 'ANY',
				role: 'ANY',
				lane: 'ANY'
			}
		);
	}
]);

dataModule.factory('ItemInfo', ['$resource',
	function($resource) {
		return $resource('/data/items/na/:patch/en_US.json', {}, {
			get: {
                method: 'GET',
                transformResponse: function(data, headers){
                	return angular.fromJson(data);
                }
            }
		});
	}
]);

dataModule.factory('ChampionInfo', ['$resource',
	function($resource) {
		return $resource('/data/champions/na/:patch/en_US.json', {}, {
			get: {
                method: 'GET',
                transformResponse: function(data, headers){
                	return angular.fromJson(data);
                }
            }
		});
	}
]);


var doransGuide = angular.module('doransGuide', ['doransData', 'ngRoute', 'ngSanitize', 'ui.bootstrap']);

var MODE_BOTH = 0;
var MODE_TIME = 1;
var MODE_GOLD = 2;

var selections = ['region', 'map', 'queue', 'champion', 'item'];
var allSelections = ['region', 'map', 'queue', 'elo', 'champion', 'item', 'role', 'lane', 'patch'];

function namedtuple(fields) {
    return function(arr) {
        var obj = { };

        _(_.zip(fields, arr))
        .each(function(i) {
        	obj[i[0]] = i[1];
        });

        return obj;
    };
};

var Configuration = namedtuple(allSelections);

function cartesianProductOf() {
    return _.reduce(arguments, function(a, b) {
        return _.flatten(_.map(a, function(x) {
            return _.map(b, function(y) {
                return x.concat([y]);
            });
        }), true);
    }, [ [] ]);
};

function inputToConfigs(input) {
	var normalizedInput = _.map(
		allSelections,
		function(x) { return _.map(input[x], function(x) { return x.id; }) || []; }
	);
	var comparedConfigs = cartesianProductOf.apply(this, normalizedInput);
	var allConfigs = _.map(comparedConfigs, Configuration);
	return allConfigs;
}

doransGuide.controller('MainCtrl', ['$scope', function ($scope) {}]);

doransGuide.controller('SearchCtrl', ['$scope', '$routeParams', 'Stats', 'ChampionInfo', 'ItemInfo',
	function ($scope, $routeParams, Stats, ChampionInfo, ItemInfo) {
		$scope.pendingConfig = {};
		allSelections.forEach(function(prop) {
			$scope.pendingConfig[prop] = [{id: "ANY"}];
		});
		selections.forEach(function(prop) {
			$scope.pendingConfig[prop] = [{id: $routeParams[prop] || "ANY"}];
		});
		$scope.pendingConfig.patch = [{id: '5.11.1'}, {id: '5.14.1'}];

		$scope.selections = selections;
		$scope.regions = [{id: 'ANY', name: 'Any Region'},
						  {id: 'br', name: 'Brasil'},
						  {id: 'na', name: 'North America'},
						  {id: 'euw', name: 'Europe'},
						  {id: 'las', name: 'Los Angeles South'},
						  {id: 'lan', name: 'Los Angeles North'},
						  {id: 'eune', name: 'Europe East'},
						  {id: 'kr', name: 'Korea'},
						  {id: 'ru', name: 'Russia'}];
		$scope.patches = [{id: 'ANY', name: 'Any Patch'},
						  {id: '5.11.1', name: 'Pre AP-Item Changes'},
						  {id: '5.14.1', name: 'Post Ap-Item Changes'}];
		$scope.maps = [{id: 'ANY', name: 'Any Map'},
					   {id: '11', name: "Summoner's Rift"}];
		$scope.queues = [{id: 'ANY', name: 'Any Queue'},
						 {id: 'normal', name: 'Normal 5x5'},
						 {id: 'ranked', name: 'Solo Ranked 5x5'}];
		$scope.elos = [{id: 'ANY', name: 'Any Elo'},
					   {id: 'gold', name: 'Gold'}];
		ChampionInfo.get({patch: '5.14.1'},
			function(champData) {
				var array = _.sortBy(champData['data'], function(d) { return d.name;})
				array.unshift(
						{id: 'ANY',
						name: 'Any'});
				$scope.champions = array;
			}
		);
		ItemInfo.get({patch: '5.14.1'},
			function(itemData) {
				var array = _.sortBy(itemData['data'], function(d) { return d.name;})
				array.unshift(
						{id: 'ANY',
						name: 'Any'});
				$scope.items = array;
			}
		);
		$scope.roles = [{id: 'ANY', name: 'Any Role'}, {id: 'tank', name: 'Tank'}];
		$scope.lanes = [{id: 'ANY', name: 'Any Lane'}, {id: 'bot', name: 'Bottom Lane'}];

		$scope.currentDatas = [];

		$scope.submit = function() {
			var currentConfigs = inputToConfigs($scope.pendingConfig);
			$scope.currentDatas = _.map(currentConfigs, function (config) {
				gold_time = {};
				gold = {};
				time = {};
				overall = {};
				Stats.get(config).$promise.then(function(data) {
					// TODO: parse the data
				});
				return {gold_time: gold_time,
						gold: gold,
						time: time,
						overall: overall
				};
			});
		};

		$scope.submit();
	}
]);

doransGuide.controller('ErrorCtrl', ['$scope', '$routeParams',
	function ($scope, $routeParams) {
		$scope.error = $routeParams.code;
	}
]);

doransGuide.filter('errorshort', function() {
	return function(error) {
		switch(parseInt(error)) {
			case 404: return "File not found";
		}
		return "Unexpected error";
	};
});

doransGuide.filter('errorlong', function() {
	return function(error) {
		switch(parseInt(error)) {
			case 404: return 'Baron has eaten the page you are searching for. Go back to <a href="/">the start page</a> and try again.';
		}
		return "Unexpected error";
	};
});

doransGuide.filter('displaymodel',
	function() {
		return function(type) {
			return '/templates/inputs/' + type + '.htm';
		}
	}
);

doransGuide.filter('dataToColor',
	function() {
		return function(data) {
			if(data === undefined || data == null) {
				return 'red';
			}
			won = data.gamesWon;
			played = data.gamesPlayed;
			ratio = won/played;
			impact = played ? 1 - 1/played : 0;
			blue = 255*ratio;
			red = 255*(1-ratio);
			return 'rgba(' + red + ', 0, ' + blue + ', ' + impact + ')';
		}
	}
);

doransGuide.directive('statViewer', function() {
	return {
		templateUrl: '/templates/data/dataView.htm'
	};
});

doransGuide.directive('champion', ['ChampionInfo', function(ChampionInfo) {
	return {
		templateUrl: '/templates/data/champion.htm',
		link: function(scope, element, attrs) {
			function updateChamp(newChamp) {
				if(!newChamp || !newChamp.image) {
					scope.champName = 'Any';
					scope.champTitle = 'the Unknown';
					scope.champImage = '/assets/images/missing.png';
					scope.champSprite = '/assets/images/missing.png';
					scope.champImgX = 0;
					scope.champImgY = 0;
					scope.champImgW = 48;
					scope.champImgH = 48;
				} else {
					var patch = '5.14.1';
					scope.champName = newChamp.name;
					scope.champTitle = newChamp.title;
					scope.champImage = 'http://ddragon.leagueoflegends.com/cdn/' + patch + '/img/champion/' + newChamp.image.full;
					scope.champSprite = 'http://ddragon.leagueoflegends.com/cdn/' + patch + '/img/sprite/' + newChamp.image.sprite;
					scope.champImgX = newChamp.image.x;
					scope.champImgY = newChamp.image.y;
					scope.champImgW = newChamp.image.w;
					scope.champImgH = newChamp.image.h;
				}
			}
			scope.$watch(attrs.lolChamp, updateChamp);
		}
	};
}]);

doransGuide.directive('itemLol', ['ItemInfo', function(ItemInfo) {
	return {
		templateUrl: '/templates/data/item.htm',
		link: function(scope, element, attrs) {
			function updateItem(item) {
					if(!item || !item.image) {
						scope.itemName = 'Any';
						scope.itemImage = 'assets/images/missing.png';
						scope.itemSprite = 'assets/images/missing.png';
						scope.itemImgX = 0;
						scope.itemImgY = 0;
						scope.itemImgW = 48;
						scope.itemImgH = 48;
					} else {
						var patch = '5.14.1';
						scope.itemName = item.name;
						scope.itemImage = 'http://ddragon.leagueoflegends.com/cdn/' + patch + '/img/item/' + item.image.full;
						scope.itemSprite = 'http://ddragon.leagueoflegends.com/cdn/' + patch + '/img/sprite/' + item.image.sprite;
						scope.itemImgX = item.image.x;
						scope.itemImgY = item.image.y;
						scope.itemImgW = item.image.w;
						scope.itemImgH = item.image.h;
					}
				}
				scope.$watch(attrs.lolItem, updateItem);
			}
	};
}]);

doransGuide.config(['$routeProvider', '$locationProvider',
	function ($routeProvider, $locationProvider) {
		$routeProvider
		.when('/', {
			templateUrl: 'templates/index.htm',
			controller: 'MainCtrl'
		})
		.when('/about', {
			templateUrl: 'templates/about.htm',
			controller: 'MainCtrl'
		})
		.when('/test', {
			templateUrl: 'templates/test.htm',
			controller: 'MainCtrl'
		})
		.when('/search', {
			templateUrl: 'templates/search.htm',
			controller: 'SearchCtrl'
		})
		.when('/search/:item', {
			templateUrl: 'templates/search.htm',
			controller: 'SearchCtrl'
		})
		.when('/error/:code', {
			templateUrl: 'templates/error.htm',
			controller: 'ErrorCtrl'
		})
		.otherwise({
			redirectTo: 'error/404'
		});
		$locationProvider.html5Mode(true);
	}
]);

