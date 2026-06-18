class CollinearTriangleBaseVectorsException(Exception):
    """Exception for collinear vectors constructing a triangle"""
    
    def __init__(self, message=""):
        self._message = message
        super().__init__(message)