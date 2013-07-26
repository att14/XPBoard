// var usernames = [
//   'atribone', 'imalison', 'anthony', 'sraveend', 'dersek', 'ssridhar',
//   'yoann', 'selston', 'cheng', 'bthiell', 'arvin', 'ychan', 'yli',
//   'clee', 'matthew', 'ywchen', 'joshua'
// ];
// $scope.statuses = ["New", "Assigned", "In Review", "Ship-It", "On Prod"]

TicketsByStatusCtrl = ['$scope', 'TicketData', function($scope, TicketData) {
  $scope.ticketsByStatus = _.groupBy(TicketData.tickets, 'status');
}];

TicketsByOwnerCtrl = ['$scope', 'TicketData', function($scope, TicketData) {
  $scope.ticketsByOwner = _.groupBy(TicketData.tickets, 'owner');
}];


ReviewsByUserCtrl = ['$scope', function($scope) {

}];

UserStatusCtrl = ['$scope', 'TicketData', function($scope, TicketData) {
  $scope.ticketsByOwner = _.groupBy(TicketData.tickets, 'owner');
  $scope.reviewRequestsByPrimary = _.groupBy(TicketData.tickets, function(ticket) {
    return ticket.review_requests.length > 0 ? ticket.review_requests[0].primary_reviewer : 'I wish this was Python';
  });
  delete $scope.reviewRequestsByPrimary['I wish this was Python'];
  $scope.title = 'Derp';
}]
