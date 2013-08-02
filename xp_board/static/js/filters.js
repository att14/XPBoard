angular.module('XPBoard').filter('ticketFilter', ['search', function(search) {
  return function(tickets) { return search.filterTickets(tickets); };
}]);
