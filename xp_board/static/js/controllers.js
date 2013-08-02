var TicketsByStatusCtrl = [
  '$scope', 'TicketData', 'status', 'search',
  function($scope, TicketData, status, search) {
    $scope.searchText = "";
    search.addFilter(function(ticket) {
      var matchers = $scope.searchText.split("|");
      return _.any(matchers, function(matcher) {
        return ticket.owner.indexOf(matcher) > -1 || (
          ticket.review_requests.length > 0 &&
            ticket.review_requests[0].primary_reviewer.indexOf(matcher) > -1
        );
      });
    });
    $scope.ticketsByStatus = [];
    setTimeout(
      function() {
        var ticketsByStatus =  _.groupBy(TicketData.tickets, 'status');
        $scope.ticketsByStatus = _.map(status.order, function(statusEnum) {
          return {
            title: status.remapping[statusEnum],
            tickets: ticketsByStatus[statusEnum]
          }
        });
        $scope.$apply();
      }, 200
    );
  }
];
