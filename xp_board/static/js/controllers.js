var TicketsByStatusCtrl = ['$scope', 'TicketData', 'status', function($scope, TicketData, status) {
  $scope.searchText = "";
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
}];

var TicketsByOwnerCtrl = ['$scope', 'TicketData', function($scope, TicketData) {
  $scope.ticketsByOwner = _.groupBy(TicketData.tickets, 'owner');
}];


var ReviewsByUserCtrl = ['$scope', function($scope) {

}];

var UserStatusCtrl = ['$scope', 'TicketData', function($scope, TicketData) {
  $scope.ticketsByOwner = _.groupBy(TicketData.tickets, 'owner');
  $scope.reviewRequestsByPrimary = _.groupBy(TicketData.tickets, function(ticket) {
    return ticket.review_requests.length > 0 ? ticket.review_requests[0].primary_reviewer : '###';
  });
  delete $scope.reviewRequestsByPrimary['###'];
}]
