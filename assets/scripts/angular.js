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
			get: function(config, succ_callback, fail_callback) {
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
				response.$promise.then(function(data) {
					var jsonData = data[fullpath];
					if(succ_callback) succ_callback(jsonData);
				}, fail_callback);
				return response;
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

var doransServices = angular.module('services',[]);
/**
 * Transforms one set of data to its color-representation.
 * The higher the percentage of won games, the more blue the color is, the lower, the red-isher. (yes, that is a word).
 * Also, with more played games, data becomes more reliable and thus the opacity grows.
 * 
 * @param data: An object with the properties 'gamesWon' and 'gamesPlayed'
 */
doransServices.filter('dataToColor',
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
 * A filter that transforms an errorcode to a useful user-output
 * @param error: the error code
 */
doransServices.filter('errorshort', function() {
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
doransServices.filter('errorlong', function() {
	return function(error) {
		switch(parseInt(error)) {
			case 404: return 'Baron has eaten the page you are searching for. Go back to <a href="/">the start page</a> and try again.';
		}
		return "Unexpected error";
	};
});
/**
 * Transforms a value into its percentage representation
 */
doransServices.filter('percentage', function() {
	return function(input, length) {
		if(!length) length = 3;
		console.log("Invoked!");
		if (isNaN(input)) {
			return input;
		}
    	return Math.floor(input * Math.pow(10, length)) / Math.pow(10, length - 2)+ '%';
	};
});

var doransGuide = angular.module('doransGuide', ['services', 'doransData', 'ngRoute', 'ngSanitize', 'ui.bootstrap']);

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
		$scope.pendingConfig.patch = [{id: '5.11'}, {id: '5.14'}];

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
						  {id: '5.11', name: 'Pre AP-Item Changes'},
						  {id: '5.14', name: 'Post Ap-Item Changes'}];
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
				var array = _.sortBy(itemData['data'], function(d) { return d.name;});
				// _.filter(array, function(d) { apItems.contains(d.id) });
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
		/**
		 * The submit button: Derive all configs the user wants to compare with each other and
		 * derive their data sets.
		 */
		$scope.submit = function() {
			$scope.currentDatas = [];
			var currentConfigs = inputToConfigs($scope.pendingConfig);
			var comparedConfigs = _.chain(allSelections)
				.map(function(s) {
					return $scope.pendingConfig[s].length > 1 ? s : undefined;
				})
				.reject(function(s) { return s === undefined; })
				.value();
			_.each(currentConfigs, function (config) {
				Stats.get(config, function(data) {
					if(!data) return;
					var title = _.chain(comparedConfigs)
						.map(function(s) {
							return "Unknown comparison";
						})
						.reduce(function(stri, name) {
							return stri + ' | ' + name;
						}, '')
						.value().substring(3);
					var viewconfig = {
						timeAndGoldTable: {
        					options: {
        					},
        					series: []
						},
						timeTable: {
							options: {

							},
							series: []
						},
						goldTable: {
							options: {

							},
							series: []
						},
						overall: {

						}
					};
					for(var i = 0; i < data.timeAndGoldTable.length; i++) {
						var time = i % 7;
						var gold = Math.floor(i / 7);
						var entry = data.timeAndGoldTable[i];
						var won = entry ? entry[1] : 0;
						var played = entry ? entry[0] : 0;
						if(time == 0)
							viewconfig.timeAndGoldTable.series.unshift([]);
						viewconfig.timeAndGoldTable.series[0].push(played != 0 ? won/played : 0);
						console.log(viewconfig.timeAndGoldTable.series);
					}
					for(var i = 0; i < data.timeTable.length; i++) {
						var entry = data.timeTable[i];
						var won = entry ? entry[1] : 0;
						var played = entry ? entry[0] : 0;
						viewconfig.timeTable.series.push(i, played != 0 ? won/played : 0);
					}
					for(var i = 0; i < data.goldTable.length; i++) {
						var entry = data.goldTable[i];
						var won = entry ? entry[1] : 0;
						var played = entry ? entry[0] : 0;
						viewconfig.goldTable.series.push(i, played != 0 ? won/played : 0);
					}
					var entry = data.winStatistic;
					var won = entry ? entry[1] : 0;
					var played = entry ? entry[0] : 0;
					viewconfig.overall.value = played != 0 ? won/played : 0;
					$scope.currentDatas.push({
						title: title,
						data: viewconfig
					});
					console.log($scope.currentDatas);
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
 * A controller that fetches data for the direct comparison on the front page
 */
doransGuide.controller('CompareCtrl', ['$q', '$scope', '$routeParams', '$resource',
	function($q, $scope, $routeParams, $resource){
		$scope.mode = $routeParams.mode || 'DIFF';
		var resource = $resource('data/analysis/ANY/:patch/ANY/ANY.ANY.json');
		$scope.sortOptions = [{id: "DIFF", name: "Winrate difference"},
								{id: "OLD", name: "Winrate in patch 5.11"},
								{id: "NEW", name: "Winrate in patch 5.14"}];
		var patch5_11p = resource.get({patch:'5.11'});
		var patch5_14p = resource.get({patch:'5.14'});
		$q.all([patch5_11p.$promise, patch5_14p.$promise])
			.then(function(result) {
				var patch5_11 = result[0];
				var patch5_14 = result[1];
				var pathForItem = function(patch, item){
					return 'ANY/' + patch + '/ANY/ANY/ANY/ANY/' +
								item + '/ANY/ANY';
				}
				var generateWinRate = function(played, won){
					if(played == 0) return 0;
					return won / played;
				}
				var retrieveItem = function(path, from){
					if(!from[path]) return[0,0];
					if(!from[path]['winStatistic']) return [0,0];
					return from[path]['winStatistic'];
				}
				var apItems = [1026, 3078, 3089, 3090, 3092, 3098, 3100, 1056, 1058, 3108, 1063, 1052, 3434, 3115, 3116, 3504, 1076, 3113, 3001, 3003, 3135, 3136, 3744, 3145, 3146, 3023, 3152, 3025, 3027, 3029, 3286, 3290, 3151, 3165, 3040, 3041, 3170, 3430, 3174, 3303, 3048, 3433, 3050, 3431, 3124, 3285, 3057, 3060, 3829, 3191, 3007, 3196, 3197, 3198, 3157]
				var generateTuple = function(item){
					var fullPath11 = pathForItem('5.11', item);
					var fullPath14 = pathForItem('5.14', item);
					var win11 = retrieveItem(fullPath11, patch5_11);
					var win14 = retrieveItem(fullPath14, patch5_14);
					var winRate11 = generateWinRate(win11[0], win11[1]);
					var winRate14 = generateWinRate(win14[0], win14[1]);
					return {itemId : item, 
							winRate11 : winRate11,
							winRate14 : winRate14,
							diff : winRate14-winRate11
							};
				}
				$scope.compareData = _.map(apItems, generateTuple);
				$scope.compareData = $scope.compareData.filter(function(item){return item.winRate11 > 0 && item.winRate14 > 0;});
			});
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
			mode: '=',
			title: '='
		},
		controller: controller,
		compile: function(element, attrs){
			if (!attrs.mode) { attrs.mode = 'TIME_GOLD'; }
		}
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

/*doransGuide.directive('heatMap', function(){
	return {
	    restrict: 'E',
	    scope: {
	        data: '='
	    },
	    template: '<div container></div>',
	    link: function(scope, ele, attr){
	        scope.heatmapInstance = h337.create({
	          container: ele.find('div')[0]
	        });
	        scope.heatmapInstance.setData(scope.data);
	    }
	};
});*/

doransGuide.config(['$routeProvider', '$locationProvider',
	function ($routeProvider, $locationProvider) {
		$routeProvider
		.when('/', {
			templateUrl: 'templates/compare.htm',
			controller: 'CompareCtrl'
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
