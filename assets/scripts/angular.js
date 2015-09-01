var selections = ['region', 'map', 'queue', 'champion', 'item'];
var allSelections = ['region', 'map', 'queue', 'elo', 'champion', 'item', 'role', 'lane', 'patch'];
/** Utility implementation for named tuples */
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

var dataModule = angular.module('doransData', ['ngResource']);
/**
 * Our factory for statistics. Offers a get method
 *
 * @param config: a Configuration object
 * @return: The statistic to the configuration
 */
dataModule.factory('Stats', ['$resource',
	function($resource) {
		return {
			get: function(config) {
				var resource = $resource('data/analysis/:region/:patch/:map/:queue.:elo.json');
				var fullpath = config.region + '/' +
						config.patch + '/' +
						config.map + '/' +
						config.queue + '/' +
						config.elo + '/' +
						config.champion + '/' +
						config.item + '/' +
						config.role + '/' +
						config.lane;
				var response = resource.get({region: config.region,
											 patch: config.patch,
											 map: config.map,
											 queue: config.queue,
											 elo: config.elo});
				var data = response[fullpath];
				console.log(data);
				return data;
			}
		}
	}
]);
/**
 * ItemInfo factory. Used to get the correct items for the selected patch.
 */
dataModule.factory('ItemInfo', ['$resource',
	function($resource) {
		return $resource('data/items/na/:patch/en_US.json', {}, {
			get: {
                method: 'GET',
                transformResponse: function(data, headers) {
                	return angular.fromJson(data);
                }
            }
		});
	}
]);
/**
 * ChampionInfo factory. Same as ItemInfo for champions
 */
dataModule.factory('ChampionInfo', ['$resource',
	function($resource) {
		return $resource('data/champions/na/:patch/en_US.json', {}, {
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
/**
 * The controller that is used in /search/.... Additional path parameters are accepted, each
 * mapped to the respectitive input.
 *
 * @pathparam region: the region-id
 * @pathparam map: the map-id, see https://developer.riotgames.com/docs/static-data
 * @pathparam queue: the queue the player used. One of https://github.com/HeroicKatora/DoransGuide/blob/master/src/lolstatic/__init__.py#QueueType
 * @pathparam elo: the elo of the queue. https://github.com/HeroicKatora/DoransGuide/blob/master/src/lolstatic/__init__.py#EloType
 * @pathparam champion: a champion-id, see https://developer.riotgames.com/docs/static-data
 * @pathparam item: an item id, see https://developer.riotgames.com/docs/static-data
 * @pathparam autoSubmit: if true, the above given request is automatically submitted, missing data defaults to 'ANY'
 */
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
						  {id: 'BR', name: 'Brasil'},
						  {id: 'NA', name: 'North America'},
						  {id: 'EUW', name: 'Europe'},
						  {id: 'LAS', name: 'Latin America South'},
						  {id: 'LAN', name: 'Latin America North'},
						  {id: 'EUNE', name: 'Europe East'},
						  {id: 'KR', name: 'Korea'},
						  {id: 'RU', name: 'Russia'},
						  {id: 'TR', name: 'Turkey'},
						  {id: 'OCE', name: 'Oceania'}];
		$scope.patches = [{id: 'ANY', name: 'Any Patch'},
						  {id: '5.11.1', name: 'Pre AP-Item Changes'},
						  {id: '5.14.1', name: 'Post Ap-Item Changes'}];
		$scope.maps = [{id: 'ANY', name: 'Any Map'},
					   {id: '11', name: "Summoner's Rift"}];
		$scope.queues = [{id: 'ANY', name: 'Any Queue'},
						 {id: 'NORMAL_5x5_BLIND', name: 'Normal 5x5'},
						 {id: 'RANKED_SOLO_5x5', name: 'Solo Ranked 5x5'}];
		$scope.elos = [{id: 'ANY', name: 'Any Elo'},
					   {id: 'CHALLENGER', name: 'Challenger'},
					   {id: 'MASTER', name: 'Master'},
					   {id: 'DIAMOND', name: 'Diamond'},
					   {id: 'PLATINUM', name: 'Platinum'},
					   {id: 'GOLD', name: 'Gold'},
					   {id: 'SILVER', name: 'Silver'},
					   {id: 'BRONZE', name: 'Bronze'},
					   {id: 'UNRANKED', name: 'No rating'}];
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
		// NEXT: if we had data from something else, it would make sense to add those queues here
		$scope.roles = [{id: 'ANY', name: 'Any Role'},
						{id: 'tank', name: 'Tank'}];
		$scope.lanes = [{id: 'ANY', name: 'Any Lane'},
						{id: 'bot', name: 'Bottom Lane'}];

		$scope.currentDatas = [];

		$scope.submit = function() {
			$scope.currentDatas = [];
			var currentConfigs = inputToConfigs($scope.pendingConfig);
			_.each(currentConfigs, function (config) {
				Stats.get(config, function(data) {

					if(!data) return;
					$scope.currentDatas.push(data);
				});
			});
			var statViewer = document.getElementById("dataview")
			if(statViewer) statViewer.scrollIntoView(true);
		};
		if($routeParams.autoSubmit) $scope.submit();
	}
]);
/**
 * The controller that handles errors.
 *
 * @pathparam code: the http-error code to set, e.g. 404
 */
doransGuide.controller('ErrorCtrl', ['$scope', '$routeParams',
	function ($scope, $routeParams) {
		$scope.error = $routeParams.code;
	}
]);
/**
 * A filter that transforms an errorcode to a useful user-output
 * @param error: the error code
 */
doransGuide.filter('errorshort', function() {
	return function(error) {
		switch(parseInt(error)) {
			case 404: return "File not found";
		}
		return "Unexpected error";
	};
});
/**
 * A filter that transforms an errorcode to a more extensive error,
 * including html. Basically it blames the error on Nashor.
 * 
 * @param error: the error code
 */
doransGuide.filter('errorlong', function() {
	return function(error) {
		switch(parseInt(error)) {
			case 404: return 'Baron has eaten the page you are searching for. Go back to <a href="/">the start page</a> and try again.';
		}
		return "Unexpected error";
	};
});
/**
 * Template for a specific input option
 */
doransGuide.filter('displaymodel',
	function() {
		return function(type) {
			return 'templates/inputs/' + type + '.htm';
		}
	}
);
/**
 * Transforms one set of data to its color-representation.
 * The higher the percentage of won games, the more blue the color is, the lower, the red-isher. (yes, that is a word).
 * Also, with more played games, data becomes more reliable and thus the opacity grows.
 * 
 * @param data: An object with the properties 'gamesWon' and 'gamesPlayed'
 */
doransGuide.filter('dataToColor',
	function() {
		return function(data) {
			if(!data) {
				return 'white';
			}
			won = data.gamesWon;
			played = data.gamesPlayed;
			ratio = won/played;
			impact = played ? 1 - 1/played : 0;
			blue = 255 * ratio;
			red = 255 * (1-ratio);
			return 'rgba(' + red + ', 0.1, ' + blue + ', ' + impact + ')';
		}
	}
);
/**
 * Initializes a stat-viewer to display data in.
 * 
 * @attribute data: the data array to display
 * @attribute mode: the display-mode, one in ['TIME_GOLD', 'GOLD', 'TIME', 'OVERALL']
 */
doransGuide.directive('statViewer', function() {
	/**
	 * A custom controller, to use the data
	 */
	var controller = ['$scope', function($scope) {
		(function init() {
			$scope.items = angular.copy($scope.datasource);
		})();
	}];

	return {
		templateUrl: 'templates/data/dataView.htm',
		scope: {
			datasource: '=data',
			mode: '='
		},
		controller: controller
	};
});
/**
 * Displays a champion-icon of the given champion
 * 
 * @attribute lolChamp: the championDTO-object to display (with an ImageDTO), see the API-docs 
 */
doransGuide.directive('champion', ['ChampionInfo', function(ChampionInfo) {
	return {
		templateUrl: 'templates/data/champion.htm',
		link: function(scope, element, attrs) {
			function updateChamp(newChamp) {
				if(!newChamp || !newChamp.image) {
					scope.champName = 'Any';
					scope.champTitle = 'the Unknown';
					scope.champImage = 'assets/images/missing.png';
					scope.champSprite = 'assets/images/missing.png';
					scope.champImgX = 0;
					scope.champImgY = 0;
					scope.champImgW = 48;
					scope.champImgH = 48;
				} else {
					var patch = '5.14.1';
					scope.champName = newChamp.name;
					scope.champTitle = newChamp.title;
					scope.champImage = 'https://ddragon.leagueoflegends.com/cdn/' + patch + '/img/champion/' + newChamp.image.full;
					scope.champSprite = 'https://ddragon.leagueoflegends.com/cdn/' + patch + '/img/sprite/' + newChamp.image.sprite;
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
/**
 * Displays a item-icon of the given item
 * 
 * @attribute lolChamp: the itemDTO-object to display (with an ImageDTO), see the API-docs
 */
doransGuide.directive('itemLol', ['ItemInfo', function(ItemInfo) {
	return {
		templateUrl: 'templates/data/item.htm',
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
						scope.itemImage = 'https://ddragon.leagueoflegends.com/cdn/' + patch + '/img/item/' + item.image.full;
						scope.itemSprite = 'https://ddragon.leagueoflegends.com/cdn/' + patch + '/img/sprite/' + item.image.sprite;
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

